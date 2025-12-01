# codegen.py - Gerador de código LLVM IR
from llvmlite import ir, binding
import llvmlite.binding as llvm
from parser import *
from tokens import TokenType
import os
import tempfile
import subprocess

class LLVMCodeGenerator:
    def __init__(self):
        # Inicialização do LLVM (removida chamada deprecated)
        try:
            llvm.initialize_native_target()
            llvm.initialize_native_asmprinter()
        except:
            pass  # Em versões mais recentes, a inicialização é automática
        
        # Criação do módulo LLVM
        self.module = ir.Module(name="main")
        self.builder = None
        self.function = None
        
        # Contador para nomes únicos de blocos
        self.block_counter = 0
        
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
            return self._generate_program(ast_node)
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
        """Gera código para declaração de função (simplificado)"""
        # Por simplicidade, vamos ignorar funções definidas pelo usuário nesta implementação
        # Em uma implementação completa, seria necessário criar a função e gerar código para o corpo
        pass
        
    def _generate_return(self, return_stmt):
        """Gera código para statement return"""
        if return_stmt.value:
            ret_value = self._generate_expression(return_stmt.value)
            if ret_value:
                # Converte para int32 se necessário
                if ret_value.type == self.double_type:
                    ret_value = self.builder.fptosi(ret_value, self.int32_type)
                elif ret_value.type == self.bool_type:
                    ret_value = self.builder.zext(ret_value, self.int32_type)
                self.builder.ret(ret_value)
        else:
            self.builder.ret(ir.Constant(self.int32_type, 0))
            
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
                
        # Continue no merge block
        self.builder.position_at_end(merge_block)
        
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
            
            # Suporte básico para println (usando puts)
            if func_name == "println":
                if len(call.args) == 1:
                    arg = self._generate_expression(call.args[0])
                    if arg.type.is_pointer:  # String
                        return self.builder.call(self.puts_func, [arg])
                    else:
                        # Converte número para string (simplificado - usa printf)
                        fmt_str = "%g\n"
                        fmt_bytes = (fmt_str + '\0').encode('utf-8')
                        fmt_type = ir.ArrayType(self.int8_type, len(fmt_bytes))
                        fmt_const = ir.Constant(fmt_type, bytearray(fmt_bytes))
                        
                        fmt_global = ir.GlobalVariable(self.module, fmt_type, name=".fmt")
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
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ll', delete=False) as f:
            f.write(str(self.module))
            ir_file = f.name
            
        try:
            # Compila usando clang
            subprocess.run(['clang', ir_file, '-o', output_file], check=True)
            print(f"Executável gerado: {output_file}")
        except subprocess.CalledProcessError as e:
            print(f"Erro na compilação: {e}")
        except FileNotFoundError:
            print("Erro: clang não encontrado. Instale o clang primeiro.")
        finally:
            # Remove arquivo temporário
            os.unlink(ir_file)
