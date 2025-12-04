# codegen.py - Gerador de código LLVM IR
from llvmlite import ir, binding
import llvmlite.binding as llvm
from parser import *
from tokens import TokenType
import os
import tempfile
import subprocess
import sys
from pathlib import Path
from enum import Enum

# Níveis de otimização
class OptimizationLevel(Enum):
    O0 = 0  # Sem otimização
    O1 = 1  # Otimizações básicas
    O2 = 2  # Otimizações moderadas  
    O3 = 3  # Otimizações agressivas
    Os = 4  # Otimizar para tamanho
    Oz = 5  # Otimizar agressivamente para tamanho

# Import explícito das classes que usamos
from parser import (
    Program, VarDecl, FuncDecl, ReturnStmt, IfStmt, Block, ExprStmt,
    WhileStmt, ForStmt, Identifier, Literal, Unary, Binary, Assign, Call
)

class LLVMCodeGenerator:
    def __init__(self, optimization_level=OptimizationLevel.O2):
        # Inicialização do LLVM (removida chamada deprecated)
        try:
            llvm.initialize_native_target()
            llvm.initialize_native_asmprinter()
        except:
            pass  # Em versões mais recentes, a inicialização é automática
        
        # Configuração de otimização
        self.optimization_level = optimization_level
        
        # Criação do módulo LLVM
        self.module = ir.Module(name="main")
        self.builder = None
        self.function = None
        
        # Contador para nomes únicos de blocos e strings
        self.block_counter = 0
        self.string_counter = 0
        
        # Tabela de símbolos (variáveis)
        self.symbol_table = {}
        self.current_scope = 0
        self.scope_stack = [{}]
        
        # Tipos LLVM básicos
        self.double_type = ir.DoubleType()
        self.int32_type = ir.IntType(32)
        self.int8_type = ir.IntType(8)
        self.void_type = ir.VoidType()
        self.bool_type = ir.IntType(1)
        
        # Funções built-in
        self._declare_builtin_functions()
        
    def _declare_builtin_functions(self):
        """Declara funções built-in como printf"""
        # printf(char*, ...)
        printf_type = ir.FunctionType(self.int32_type, [ir.PointerType(self.int8_type)], var_arg=True)
        self.printf_func = ir.Function(self.module, printf_type, name="printf")
        
        # puts(char*)
        puts_type = ir.FunctionType(self.int32_type, [ir.PointerType(self.int8_type)])
        self.puts_func = ir.Function(self.module, puts_type, name="puts")
        
    def _enter_scope(self):
        """Entra em um novo escopo"""
        self.current_scope += 1
        self.scope_stack.append({})
        
    def _exit_scope(self):
        """Sai do escopo atual"""
        if len(self.scope_stack) > 1:
            self.scope_stack.pop()
            self.current_scope -= 1
            
    def _add_variable(self, name, alloca_inst):
        """Adiciona variável ao escopo atual"""
        self.scope_stack[-1][name] = alloca_inst
        
    def _get_variable(self, name):
        """Busca variável nos escopos (do mais recente ao mais antigo)"""
        for scope in reversed(self.scope_stack):
            if name in scope:
                return scope[name]
        return None
        
    def generate_code(self, ast_node):
        """Gera código LLVM IR para o AST"""
        if isinstance(ast_node, Program):
            # Gera código não otimizado
            ir_code = self._generate_program(ast_node)
            
            # Aplica otimizações se necessário
            if self.optimization_level != OptimizationLevel.O0:
                self._optimize_module()
            
            return ir_code
        else:
            raise ValueError(f"Tipo de nó AST não suportado: {type(ast_node)}")
            
    def _generate_program(self, program_node):
        """Gera código para o programa principal"""
        # Cria função main
        main_type = ir.FunctionType(self.int32_type, [])
        main_func = ir.Function(self.module, main_type, name="main")
        block = main_func.append_basic_block(name="entry")
        self.builder = ir.IRBuilder(block)
        self.function = main_func
        
        # Gera código para todos os statements
        for stmt in program_node.statements:
            self._generate_statement(stmt)
            
        # Sempre adiciona return 0 no final se o bloco não foi terminado
        current_block = self.builder.block
        if not current_block.is_terminated:
            self.builder.ret(ir.Constant(self.int32_type, 0))
            
        return str(self.module)
        
    def _generate_statement(self, stmt):
        """Gera código para um statement"""
        if isinstance(stmt, VarDecl):
            return self._generate_var_decl(stmt)
        elif isinstance(stmt, FuncDecl):
            return self._generate_func_decl(stmt)
        elif isinstance(stmt, ReturnStmt):
            return self._generate_return(stmt)
        elif isinstance(stmt, IfStmt):
            return self._generate_if(stmt)
        elif isinstance(stmt, WhileStmt):
            return self._generate_while(stmt)
        elif isinstance(stmt, ForStmt):
            return self._generate_for(stmt)
        elif isinstance(stmt, ExprStmt):
            return self._generate_expression(stmt.expr)
        elif isinstance(stmt, Block):
            return self._generate_block(stmt)
        else:
            raise ValueError(f"Tipo de statement não suportado: {type(stmt)}")
            
    def _generate_var_decl(self, var_decl):
        """Gera código para declaração de variável"""
        var_name = var_decl.name.name
        
        # Determina o tipo baseado no inicializador
        var_type = self.double_type  # Padrão
        if var_decl.initializer:
            if isinstance(var_decl.initializer, Literal):
                if isinstance(var_decl.initializer.value, str):
                    var_type = ir.PointerType(self.int8_type)
                elif isinstance(var_decl.initializer.value, bool):
                    var_type = self.bool_type
                else:
                    var_type = self.double_type
        
        # Aloca espaço na stack
        alloca_inst = self.builder.alloca(var_type, name=var_name)
        self._add_variable(var_name, alloca_inst)
        
        # Se há inicializador, gera código e armazena
        if var_decl.initializer:
            init_value = self._generate_expression(var_decl.initializer)
            if init_value:
                # Conversão de tipos apenas se necessário
                if var_type == self.double_type and init_value.type != self.double_type:
                    if init_value.type == self.int32_type:
                        init_value = self.builder.sitofp(init_value, self.double_type)
                    elif init_value.type == self.bool_type:
                        init_value = self.builder.uitofp(init_value, self.double_type)
                elif var_type == self.bool_type and init_value.type != self.bool_type:
                    if init_value.type == self.double_type:
                        zero = ir.Constant(self.double_type, 0.0)
                        init_value = self.builder.fcmp_unordered('!=', init_value, zero)
                # Para strings, armazena diretamente
                self.builder.store(init_value, alloca_inst)
        else:
            # Inicializa com valor padrão
            if var_type == self.double_type:
                self.builder.store(ir.Constant(self.double_type, 0.0), alloca_inst)
            elif var_type == self.bool_type:
                self.builder.store(ir.Constant(self.bool_type, False), alloca_inst)
            # Para ponteiros, inicializa com null
            elif var_type.is_pointer:
                self.builder.store(ir.Constant(var_type, None), alloca_inst)
            
        return alloca_inst
        
    def _generate_func_decl(self, func_decl):
        """Gera código para declaração de função"""
        func_name = func_decl.name.name
        
        # Define tipos dos parâmetros (todos como double por simplicidade)
        param_types = [self.double_type] * len(func_decl.params)
        
        # Tipo da função (retorna double)
        func_type = ir.FunctionType(self.double_type, param_types)
        
        # Cria a função
        func = ir.Function(self.module, func_type, name=func_name)
        
        # Nomeia parâmetros
        for i, param in enumerate(func_decl.params):
            func.args[i].name = param.name
        
        # Cria bloco de entrada
        entry_block = func.append_basic_block(name="entry")
        
        # Salva estado atual
        old_builder = self.builder
        old_function = self.function
        
        # Novo builder para esta função
        self.builder = ir.IRBuilder(entry_block)
        self.function = func
        
        # Entra em novo escopo
        self._enter_scope()
        
        # Aloca espaço para parâmetros no stack e os carrega
        for i, param in enumerate(func_decl.params):
            param_name = param.name
            param_alloca = self.builder.alloca(self.double_type, name=param_name)
            self.builder.store(func.args[i], param_alloca)
            self._add_variable(param_name, param_alloca)
        
        # Gera código do corpo da função
        self._generate_statement(func_decl.body)
        
        # Se o bloco não foi terminado com return, adiciona return 0.0
        if not self.builder.block.is_terminated:
            self.builder.ret(ir.Constant(self.double_type, 0.0))
        
        # Sai do escopo
        self._exit_scope()
        
        # Restaura estado anterior
        self.builder = old_builder
        self.function = old_function
        
        return func
        
    def _generate_return(self, return_stmt):
        """Gera código para statement return"""
        # Verifica se o bloco já foi terminado
        if self.builder.block.is_terminated:
            return
            
        if return_stmt.value:
            ret_value = self._generate_expression(return_stmt.value)
            if ret_value:
                # Se estamos na função main, converte para int32
                if self.function.name == "main":
                    if ret_value.type == self.double_type:
                        ret_value = self.builder.fptosi(ret_value, self.int32_type)
                    elif ret_value.type == self.bool_type:
                        ret_value = self.builder.zext(ret_value, self.int32_type)
                    self.builder.ret(ret_value)
                else:
                    # Para funções definidas pelo usuário, converte para double
                    if ret_value.type == self.int32_type:
                        ret_value = self.builder.sitofp(ret_value, self.double_type)
                    elif ret_value.type == self.bool_type:
                        ret_value = self.builder.uitofp(ret_value, self.double_type)
                    self.builder.ret(ret_value)
        else:
            # Retorno vazio
            if self.function.name == "main":
                self.builder.ret(ir.Constant(self.int32_type, 0))
            else:
                self.builder.ret(ir.Constant(self.double_type, 0.0))
            
    def _generate_if(self, if_stmt):
        """Gera código para statement if"""
        # Avalia condição
        cond_value = self._generate_expression(if_stmt.condition)
        
        # Converte para bool se necessário
        if cond_value.type == self.double_type:
            zero = ir.Constant(self.double_type, 0.0)
            cond_value = self.builder.fcmp_unordered('!=', cond_value, zero)
        elif cond_value.type == self.int32_type:
            zero = ir.Constant(self.int32_type, 0)
            cond_value = self.builder.icmp_signed('!=', cond_value, zero)
            
        # Cria blocos básicos com nomes únicos
        self.block_counter += 1
        counter = self.block_counter
        
        then_block = self.function.append_basic_block(name=f"if_then_{counter}")
        else_block = self.function.append_basic_block(name=f"if_else_{counter}") if if_stmt.else_branch else None
        merge_block = self.function.append_basic_block(name=f"if_merge_{counter}")
        
        # Branch condicional
        if else_block:
            self.builder.cbranch(cond_value, then_block, else_block)
        else:
            self.builder.cbranch(cond_value, then_block, merge_block)
            
        # Gera código do then
        self.builder.position_at_end(then_block)
        self._generate_statement(if_stmt.then_branch)
        if not then_block.is_terminated:
            self.builder.branch(merge_block)
            
        # Gera código do else (se existir)
        if else_block:
            self.builder.position_at_end(else_block)
            self._generate_statement(if_stmt.else_branch)
            if not else_block.is_terminated:
                self.builder.branch(merge_block)
        
        # Posiciona builder no bloco merge para continuar
        self.builder.position_at_end(merge_block)
                
    def _generate_while(self, while_stmt):
        """Gera código para loop while"""
        # Cria blocos básicos com nomes únicos
        self.block_counter += 1
        counter = self.block_counter
        
        cond_block = self.function.append_basic_block(name=f"while_cond_{counter}")
        body_block = self.function.append_basic_block(name=f"while_body_{counter}")
        end_block = self.function.append_basic_block(name=f"while_end_{counter}")
        
        # Branch para o bloco de condição
        self.builder.branch(cond_block)
        
        # Gera código da condição
        self.builder.position_at_end(cond_block)
        cond_value = self._generate_expression(while_stmt.condition)
        
        # Converte para bool se necessário
        if cond_value.type == self.double_type:
            zero = ir.Constant(self.double_type, 0.0)
            cond_value = self.builder.fcmp_unordered('!=', cond_value, zero)
        elif cond_value.type == self.int32_type:
            zero = ir.Constant(self.int32_type, 0)
            cond_value = self.builder.icmp_signed('!=', cond_value, zero)
        
        # Branch condicional
        self.builder.cbranch(cond_value, body_block, end_block)
        
        # Gera código do corpo
        self.builder.position_at_end(body_block)
        self._enter_scope()
        self._generate_statement(while_stmt.body)
        self._exit_scope()
        
        # Branch de volta para a condição (se o bloco não foi terminado)
        if not self.builder.block.is_terminated:
            self.builder.branch(cond_block)
        
        # Continue no bloco final
        self.builder.position_at_end(end_block)
        
    def _generate_while(self, while_stmt):
        """Gera código para loop while"""
        # Cria blocos básicos com nomes únicos
        self.block_counter += 1
        counter = self.block_counter
        
        cond_block = self.function.append_basic_block(name=f"while_cond_{counter}")
        body_block = self.function.append_basic_block(name=f"while_body_{counter}")
        end_block = self.function.append_basic_block(name=f"while_end_{counter}")
        
        # Branch para o bloco de condição
        self.builder.branch(cond_block)
        
        # Gera código da condição
        self.builder.position_at_end(cond_block)
        cond_value = self._generate_expression(while_stmt.condition)
        
        # Converte para bool se necessário
        if cond_value.type == self.double_type:
            zero = ir.Constant(self.double_type, 0.0)
            cond_value = self.builder.fcmp_unordered('!=', cond_value, zero)
        elif cond_value.type == self.int32_type:
            zero = ir.Constant(self.int32_type, 0)
            cond_value = self.builder.icmp_signed('!=', cond_value, zero)
        
        # Branch condicional
        self.builder.cbranch(cond_value, body_block, end_block)
        
        # Gera código do corpo
        self.builder.position_at_end(body_block)
        self._enter_scope()
        self._generate_statement(while_stmt.body)
        self._exit_scope()
        
        # Branch de volta para a condição (se o bloco não foi terminado)
        if not self.builder.block.is_terminated:
            self.builder.branch(cond_block)
        
        # Continue no bloco final
        self.builder.position_at_end(end_block)
        
    def _generate_for(self, for_stmt):
        """Gera código para loop for"""
        # Entra em novo escopo para a inicialização
        self._enter_scope()
        
        # Gera código de inicialização
        if for_stmt.init:
            self._generate_statement(for_stmt.init)
        
        # Cria blocos básicos com nomes únicos
        self.block_counter += 1
        counter = self.block_counter
        
        cond_block = self.function.append_basic_block(name=f"for_cond_{counter}")
        body_block = self.function.append_basic_block(name=f"for_body_{counter}")
        inc_block = self.function.append_basic_block(name=f"for_inc_{counter}")
        end_block = self.function.append_basic_block(name=f"for_end_{counter}")
        
        # Branch para o bloco de condição
        self.builder.branch(cond_block)
        
        # Gera código da condição
        self.builder.position_at_end(cond_block)
        if for_stmt.condition:
            cond_value = self._generate_expression(for_stmt.condition)
            
            # Converte para bool se necessário
            if cond_value.type == self.double_type:
                zero = ir.Constant(self.double_type, 0.0)
                cond_value = self.builder.fcmp_unordered('!=', cond_value, zero)
            elif cond_value.type == self.int32_type:
                zero = ir.Constant(self.int32_type, 0)
                cond_value = self.builder.icmp_signed('!=', cond_value, zero)
            
            # Branch condicional
            self.builder.cbranch(cond_value, body_block, end_block)
        else:
            # Sem condição = loop infinito (vai direto pro corpo)
            self.builder.branch(body_block)
        
        # Gera código do corpo
        self.builder.position_at_end(body_block)
        self._generate_statement(for_stmt.body)
        
        # Branch para incremento (se o bloco não foi terminado)
        if not self.builder.block.is_terminated:
            self.builder.branch(inc_block)
        
        # Gera código de incremento
        self.builder.position_at_end(inc_block)
        if for_stmt.increment:
            self._generate_expression(for_stmt.increment)
        
        # Branch de volta para a condição
        self.builder.branch(cond_block)
        
        # Continue no bloco final
        self.builder.position_at_end(end_block)
        
        # Sai do escopo
        self._exit_scope()
        
    def _generate_block(self, block):
        """Gera código para um bloco"""
        self._enter_scope()
        for stmt in block.statements:
            self._generate_statement(stmt)
        self._exit_scope()
        
    def _generate_expression(self, expr):
        """Gera código para uma expressão"""
        if isinstance(expr, Literal):
            return self._generate_literal(expr)
        elif isinstance(expr, Identifier):
            return self._generate_identifier(expr)
        elif isinstance(expr, Binary):
            return self._generate_binary(expr)
        elif isinstance(expr, Unary):
            return self._generate_unary(expr)
        elif isinstance(expr, Assign):
            return self._generate_assign(expr)
        elif isinstance(expr, Call):
            return self._generate_call(expr)
        else:
            raise ValueError(f"Tipo de expressão não suportado: {type(expr)}")
            
    def _generate_literal(self, literal):
        """Gera código para literal"""
        value = literal.value
        if isinstance(value, (int, float)):
            return ir.Constant(self.double_type, float(value))
        elif isinstance(value, bool):
            return ir.Constant(self.bool_type, value)
        elif isinstance(value, str):
            # Corrige problema com encoding UTF-8
            try:
                string_bytes = (value + '\0').encode('utf-8')
                string_type = ir.ArrayType(self.int8_type, len(string_bytes))
                string_const = ir.Constant(string_type, bytearray(string_bytes))
                
                # Cria global variable com nome único
                import time
                global_name = f".str.{int(time.time() * 1000000) % 1000000}"
                string_global = ir.GlobalVariable(self.module, string_type, name=global_name)
                string_global.linkage = 'private'
                string_global.global_constant = True
                string_global.initializer = string_const
                
                # Retorna pointer para o primeiro elemento
                return self.builder.gep(string_global, [ir.Constant(self.int32_type, 0), ir.Constant(self.int32_type, 0)])
            except UnicodeEncodeError:
                # Fallback para strings com caracteres especiais
                safe_string = value.encode('ascii', 'replace').decode('ascii')
                string_bytes = (safe_string + '\0').encode('ascii')
                string_type = ir.ArrayType(self.int8_type, len(string_bytes))
                string_const = ir.Constant(string_type, bytearray(string_bytes))
                
                import time
                global_name = f".str.{int(time.time() * 1000000) % 1000000}"
                string_global = ir.GlobalVariable(self.module, string_type, name=global_name)
                string_global.linkage = 'private'
                string_global.global_constant = True
                string_global.initializer = string_const
                
                return self.builder.gep(string_global, [ir.Constant(self.int32_type, 0), ir.Constant(self.int32_type, 0)])
        else:
            raise ValueError(f"Tipo de literal não suportado: {type(value)}")
            
    def _generate_identifier(self, identifier):
        """Gera código para identificador (carrega valor da variável)"""
        var_name = identifier.name
        alloca_inst = self._get_variable(var_name)
        if alloca_inst is None:
            raise ValueError(f"Variável não declarada: {var_name}")
        return self.builder.load(alloca_inst, name=var_name)
        
    def _generate_binary(self, binary):
        """Gera código para expressão binária"""
        left = self._generate_expression(binary.left)
        right = self._generate_expression(binary.right)
        
        # Converte ambos para double para simplificar
        if left.type == self.int32_type:
            left = self.builder.sitofp(left, self.double_type)
        elif left.type == self.bool_type:
            left = self.builder.uitofp(left, self.double_type)
            
        if right.type == self.int32_type:
            right = self.builder.sitofp(right, self.double_type)
        elif right.type == self.bool_type:
            right = self.builder.uitofp(right, self.double_type)
            
        op = binary.operator
        
        # Operações aritméticas
        if op == '+':
            return self.builder.fadd(left, right, name="addtmp")
        elif op == '-':
            return self.builder.fsub(left, right, name="subtmp")
        elif op == '*':
            return self.builder.fmul(left, right, name="multmp")
        elif op == '/':
            return self.builder.fdiv(left, right, name="divtmp")
        elif op == '%':
            return self.builder.frem(left, right, name="modtmp")
        # Operações de comparação
        elif op == '<':
            return self.builder.fcmp_unordered('<', left, right, name="cmptmp")
        elif op == '>':
            return self.builder.fcmp_unordered('>', left, right, name="cmptmp")
        elif op == '<=':
            return self.builder.fcmp_unordered('<=', left, right, name="cmptmp")
        elif op == '>=':
            return self.builder.fcmp_unordered('>=', left, right, name="cmptmp")
        elif op == '==':
            return self.builder.fcmp_unordered('==', left, right, name="cmptmp")
        elif op == '!=':
            return self.builder.fcmp_unordered('!=', left, right, name="cmptmp")
        # Operações lógicas
        elif op == '&&':
            # Converte para bool
            zero = ir.Constant(self.double_type, 0.0)
            left_bool = self.builder.fcmp_unordered('!=', left, zero)
            right_bool = self.builder.fcmp_unordered('!=', right, zero)
            return self.builder.and_(left_bool, right_bool, name="andtmp")
        elif op == '||':
            # Converte para bool
            zero = ir.Constant(self.double_type, 0.0)
            left_bool = self.builder.fcmp_unordered('!=', left, zero)
            right_bool = self.builder.fcmp_unordered('!=', right, zero)
            return self.builder.or_(left_bool, right_bool, name="ortmp")
        else:
            raise ValueError(f"Operador binário não suportado: {op}")
            
    def _generate_unary(self, unary):
        """Gera código para expressão unária"""
        operand = self._generate_expression(unary.right)
        op = unary.operator
        
        if op == '-':
            if operand.type == self.double_type:
                return self.builder.fsub(ir.Constant(self.double_type, 0.0), operand, name="negtmp")
            elif operand.type == self.int32_type:
                return self.builder.sub(ir.Constant(self.int32_type, 0), operand, name="negtmp")
        elif op == '!':
            if operand.type == self.double_type:
                zero = ir.Constant(self.double_type, 0.0)
                return self.builder.fcmp_unordered('==', operand, zero, name="nottmp")
            elif operand.type == self.bool_type:
                return self.builder.not_(operand, name="nottmp")
            elif operand.type == self.int32_type:
                zero = ir.Constant(self.int32_type, 0)
                return self.builder.icmp_signed('==', operand, zero, name="nottmp")
        else:
            raise ValueError(f"Operador unário não suportado: {op}")
            
    def _generate_assign(self, assign):
        """Gera código para atribuição"""
        if not isinstance(assign.left, Identifier):
            raise ValueError("Atribuição só suportada para identificadores")
            
        var_name = assign.left.name
        alloca_inst = self._get_variable(var_name)
        if alloca_inst is None:
            raise ValueError(f"Variável não declarada: {var_name}")
            
        value = self._generate_expression(assign.value)
        
        # Verifica se os tipos são compatíveis
        var_type = alloca_inst.type.pointee
        
        # Converte tipos se necessário
        if var_type == self.double_type and value.type != self.double_type:
            if value.type == self.int32_type:
                value = self.builder.sitofp(value, self.double_type)
            elif value.type == self.bool_type:
                value = self.builder.uitofp(value, self.double_type)
        elif var_type == self.bool_type and value.type != self.bool_type:
            if value.type == self.double_type:
                zero = ir.Constant(self.double_type, 0.0)
                value = self.builder.fcmp_unordered('!=', value, zero)
        # Para outros tipos, assumir compatibilidade
            
        self.builder.store(value, alloca_inst)
        return value
        
    def _generate_call(self, call):
        """Gera código para chamada de função"""
        if isinstance(call.callee, Identifier):
            func_name = call.callee.name
            
            # Suporte para funções built-in
            if func_name == "println" or func_name == "print":
                if len(call.args) == 1:
                    arg = self._generate_expression(call.args[0])
                    if arg.type.is_pointer:  # String
                        return self.builder.call(self.puts_func, [arg])
                    else:
                        # Converte número para string (simplificado - usa printf)
                        if func_name == "println":
                            fmt_str = "%g\n"
                        else:
                            fmt_str = "%g"
                        
                        fmt_bytes = (fmt_str + '\0').encode('utf-8')
                        fmt_type = ir.ArrayType(self.int8_type, len(fmt_bytes))
                        fmt_const = ir.Constant(fmt_type, bytearray(fmt_bytes))
                        
                        # Nome único para cada formato string
                        self.string_counter += 1
                        fmt_global = ir.GlobalVariable(self.module, fmt_type, name=f".fmt{self.string_counter}")
                        fmt_global.linkage = 'private'
                        fmt_global.global_constant = True
                        fmt_global.initializer = fmt_const
                        fmt_ptr = self.builder.gep(fmt_global, [ir.Constant(self.int32_type, 0), ir.Constant(self.int32_type, 0)])
                        
                        # Converte arg para double se necessário
                        if arg.type == self.int32_type:
                            arg = self.builder.sitofp(arg, self.double_type)
                        elif arg.type == self.bool_type:
                            arg = self.builder.uitofp(arg, self.double_type)
                            
                        return self.builder.call(self.printf_func, [fmt_ptr, arg])
            
            # Suporte para funções definidas pelo usuário
            # Procura a função no módulo
            try:
                func = self.module.get_global(func_name)
                if func is not None:
                    # Gera argumentos
                    args = []
                    for arg_expr in call.args:
                        arg_value = self._generate_expression(arg_expr)
                        
                        # Converte para double se necessário
                        if arg_value.type == self.int32_type:
                            arg_value = self.builder.sitofp(arg_value, self.double_type)
                        elif arg_value.type == self.bool_type:
                            arg_value = self.builder.uitofp(arg_value, self.double_type)
                        
                        args.append(arg_value)
                    
                    # Chama a função
                    return self.builder.call(func, args, name="calltmp")
            except:
                pass
                        
        raise ValueError(f"Chamada de função não suportada: {call}")
        
    def compile_to_object(self, output_file):
        """Compila o módulo LLVM para arquivo objeto"""
        # Cria target machine
        target = llvm.Target.from_default_triple()
        target_machine = target.create_target_machine()
        
        # Compila para arquivo objeto
        with open(output_file, 'wb') as f:
            f.write(target_machine.emit_object(llvm.parse_assembly(str(self.module))))
            
    def compile_to_executable(self, output_file):
        """Compila o módulo LLVM para executável"""
        # Salva IR em arquivo temporário
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ll', delete=False, encoding='utf-8') as f:
            f.write(str(self.module))
            ir_file = f.name
            
        try:
            # Constrói comando base do clang
            clang_cmd = ['clang', ir_file, '-o', output_file, '-lm']
            
            # Adiciona flags de otimização baseadas no nível
            opt_flags = self._get_clang_optimization_flags()
            clang_cmd.extend(opt_flags)
            
            # Detecta plataforma e ajusta comando
            if sys.platform.startswith('win'):
                if not output_file.endswith('.exe'):
                    output_file += '.exe'
                    clang_cmd[2] = output_file  # Atualiza nome do arquivo de saída
            
            if self.optimization_level != OptimizationLevel.O0:
                print(f"🚀 Compilando com otimizações {self.optimization_level.name}...")
            
            # Compila usando clang
            result = subprocess.run(clang_cmd, check=True, capture_output=True, text=True)
            print(f"✅ Executável gerado: {output_file}")
            
            # Torna executável no Linux/macOS
            if not sys.platform.startswith('win'):
                os.chmod(output_file, 0o755)
                
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Erro na compilação: {e}")
            if e.stderr:
                print(f"Stderr: {e.stderr}")
            return False
        except FileNotFoundError:
            print("❌ Erro: clang não encontrado. Instale o clang primeiro.")
            print("\n📦 Para instalar:")
            if sys.platform.startswith('linux'):
                print("  Ubuntu/Debian: sudo apt install clang")
                print("  Fedora/RHEL: sudo dnf install clang")
            elif sys.platform == 'darwin':
                print("  macOS: brew install llvm")
            elif sys.platform.startswith('win'):
                print("  Windows: choco install llvm")
            return False
        finally:
            # Remove arquivo temporário
            try:
                os.unlink(ir_file)
            except:
                pass
    
    def _optimize_module(self):
        """Aplica otimizações LLVM ao módulo baseado no nível configurado"""
        # Note: As otimizações agora são aplicadas durante a compilação com clang
        # usando flags específicas em compile_to_executable
        print(f"✅ Configurado para otimizações (nível {self.optimization_level.name})")
        print("   Otimizações serão aplicadas durante a compilação com Clang")
    
    def _get_clang_optimization_flags(self):
        """Retorna flags de otimização apropriadas para o Clang"""
        level = self.optimization_level
        
        if level == OptimizationLevel.O0:
            return ['-O0']  # Sem otimizações
        elif level == OptimizationLevel.O1:
            return ['-O1']  # Otimizações básicas
        elif level == OptimizationLevel.O2:
            return ['-O2']  # Otimizações moderadas (padrão recomendado)
        elif level == OptimizationLevel.O3:
            return ['-O3']  # Otimizações agressivas
        elif level == OptimizationLevel.Os:
            return ['-Os']  # Otimizar para tamanho
        elif level == OptimizationLevel.Oz:
            return ['-Oz']  # Otimizar agressivamente para tamanho
        else:
            return ['-O2']  # Fallback para O2
    
    def _get_llvm_opt_level(self):
        """Converte nível de otimização para formato LLVM"""
        mapping = {
            OptimizationLevel.O0: 0,
            OptimizationLevel.O1: 1,
            OptimizationLevel.O2: 2,
            OptimizationLevel.O3: 3,
            OptimizationLevel.Os: 2,  # Similar a O2 mas com foco em tamanho
            OptimizationLevel.Oz: 2   # Similar a O2 mas com foco agressivo em tamanho
        }
        return mapping.get(self.optimization_level, 2)
    
    def _configure_optimization_passes(self, pass_manager):
        """Configura passes de otimização específicos baseado no nível"""
        level = self.optimization_level
        
        if level == OptimizationLevel.O0:
            # Sem otimizações
            return
        
        # Passes básicos para O1+
        if level.value >= 1:
            # Otimizações básicas de expressão
            pass_manager.add_instruction_combining_pass()
            pass_manager.add_reassociate_expressions_pass()
            pass_manager.add_gvn_pass()  # Global Value Numbering
            pass_manager.add_cfg_simplification_pass()
        
        # Passes moderados para O2+
        if level.value >= 2:
            # Otimizações de função
            pass_manager.add_function_inlining_pass(225)  # Limite de threshold
            pass_manager.add_dead_arg_elimination_pass()
            pass_manager.add_function_attrs_pass()
            
            # Otimizações de loop
            pass_manager.add_loop_vectorize_pass()
            pass_manager.add_loop_unroll_pass()
            
            # Otimizações de memória
            pass_manager.add_memcpy_optimization_pass()
            pass_manager.add_scalarize_masked_memory_intrinsics_pass()
        
        # Passes agressivos para O3
        if level == OptimizationLevel.O3:
            # Otimizações mais agressivas
            pass_manager.add_argument_promotion_pass()
            pass_manager.add_ipsccp_pass()  # Interprocedural Sparse Conditional Constant Propagation
            pass_manager.add_function_inlining_pass(325)  # Threshold maior
            
        # Passes para otimização de tamanho
        if level in [OptimizationLevel.Os, OptimizationLevel.Oz]:
            # Foca em reduzir tamanho do código
            pass_manager.add_cfg_simplification_pass()
            pass_manager.add_dead_code_elimination_pass()
            
    def get_optimization_stats(self):
        """Retorna estatísticas sobre as otimizações aplicadas"""
        try:
            module_str = str(self.module)
            functions_count = module_str.count('define ')
            globals_count = module_str.count('@')
            
            return {
                'optimization_level': self.optimization_level.name,
                'module_size': len(module_str),
                'functions_count': functions_count,
                'globals_count': globals_count
            }
        except Exception:
            return {
                'optimization_level': self.optimization_level.name,
                'module_size': len(str(self.module)),
                'functions_count': 0,
                'globals_count': 0
            }
    
    def set_optimization_level(self, level):
        """Permite alterar o nível de otimização"""
        if isinstance(level, str):
            level = OptimizationLevel[level]
        elif isinstance(level, int):
            level_map = {0: OptimizationLevel.O0, 1: OptimizationLevel.O1, 
                        2: OptimizationLevel.O2, 3: OptimizationLevel.O3}
            level = level_map.get(level, OptimizationLevel.O2)
        
        self.optimization_level = level
        print(f"🎛️ Nível de otimização definido para: {level.name}")
        
    def compile_optimized(self, output_file, show_stats=False):
        """Compila com relatório de otimizações"""
        if show_stats:
            stats_before = self.get_optimization_stats()
            print(f"\n📊 ANTES DA OTIMIZAÇÃO:")
            print(f"   Nível: {stats_before['optimization_level']}")
            print(f"   Tamanho do módulo: {stats_before['module_size']} caracteres")
            print(f"   Funções: {stats_before['functions_count']}")
            print(f"   Variáveis globais: {stats_before['globals_count']}")
        
        # Aplica otimizações se não foram aplicadas ainda
        if self.optimization_level != OptimizationLevel.O0:
            self._optimize_module()
        
        # Compila normalmente
        result = self.compile_to_executable(output_file)
        
        if show_stats and result:
            stats_after = self.get_optimization_stats()
            print(f"\n📈 APÓS OTIMIZAÇÃO:")
            print(f"   Tamanho do módulo: {stats_after['module_size']} caracteres")
            print(f"   Funções: {stats_after['functions_count']}")
            print(f"   Variáveis globais: {stats_after['globals_count']}")
            
            size_diff = stats_before['module_size'] - stats_after['module_size']
            if size_diff > 0:
                print(f"   💾 Redução de tamanho: {size_diff} caracteres ({size_diff/stats_before['module_size']*100:.1f}%)")
            
        return result
