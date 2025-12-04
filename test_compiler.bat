@echo off
REM 🧪 Script de Teste do Compilador - Windows
REM Testa todos os exemplos e valida o funcionamento

echo 🧪 TESTE AUTOMATIZADO DO COMPILADOR
echo =================================================

REM Verifica se Python está disponível
python --version >nul 2>&1
if %errorlevel% neq 0 (
    python3 --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo ❌ Python não encontrado!
        exit /b 1
    ) else (
        set PYTHON_CMD=python3
    )
) else (
    set PYTHON_CMD=python
)

echo ✅ Python encontrado: %PYTHON_CMD%

REM Verifica dependências
echo.
echo 1. Verificando Dependências...

%PYTHON_CMD% -c "import llvmlite" >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ llvmlite não encontrado!
    echo Instale com: pip install llvmlite
    exit /b 1
) else (
    echo ✅ llvmlite disponível
)

clang --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ clang não encontrado!
    echo Instale clang primeiro
    exit /b 1
) else (
    echo ✅ clang disponível
)

REM Testa exemplos com sucesso
echo.
echo 2. Testando Exemplos com Sucesso...

set success_count=0
set total_success=5

for %%f in (exemplo_sucesso_simples.js exemplo_sucesso_condicional.js exemplo_sucesso_funcoes.js exemplo_sucesso_loops.js exemplo_complexo.js) do (
    echo   Testando %%f... 
    
    if exist "exemplos\%%f" (
        %PYTHON_CMD% compile.py "exemplos\%%f" -o "test_output" >nul 2>&1
        if %errorlevel% equ 0 (
            echo   ✅ OK
            set /a success_count+=1
            del /f /q test_output test_output.exe >nul 2>&1
        ) else (
            echo   ❌ FALHOU
        )
    ) else (
        echo   ⚠️ Arquivo não encontrado
    )
)

echo   Sucessos: %success_count%/%total_success%

REM Testa exemplos com erro
echo.
echo 3. Testando Exemplos com Erro...

set error_count=0
set total_errors=3

for %%f in (exemplo_erro_sintaxe.js exemplo_erro_semantico.js exemplo_erro_escopo.js) do (
    echo   Testando %%f...
    
    if exist "exemplos\%%f" (
        %PYTHON_CMD% compile.py "exemplos\%%f" -o "test_error_output" >nul 2>&1
        if %errorlevel% equ 0 (
            echo   ❌ DEVERIA FALHAR
        ) else (
            echo   ✅ Falhou corretamente
            set /a error_count+=1
        )
        del /f /q test_error_output test_error_output.exe >nul 2>&1
    ) else (
        echo   ⚠️ Arquivo não encontrado
    )
)

echo   Erros detectados: %error_count%/%total_errors%

REM Testa funcionalidades específicas
echo.
echo 4. Testando Funcionalidades Específicas...

echo   Teste --tokens...
%PYTHON_CMD% compile.py exemplos\exemplo_sucesso_simples.js --tokens >nul 2>&1
if %errorlevel% equ 0 (
    echo   ✅ OK
) else (
    echo   ❌ FALHOU
)

echo   Teste --ast...
%PYTHON_CMD% compile.py exemplos\exemplo_sucesso_simples.js --ast >nul 2>&1
if %errorlevel% equ 0 (
    echo   ✅ OK
) else (
    echo   ❌ FALHOU
)

echo   Teste --ir...
%PYTHON_CMD% compile.py exemplos\exemplo_sucesso_simples.js --ir >nul 2>&1
if %errorlevel% equ 0 (
    echo   ✅ OK
) else (
    echo   ❌ FALHOU
)

echo   Teste --no-compile...
%PYTHON_CMD% compile.py exemplos\exemplo_sucesso_simples.js --no-compile >nul 2>&1
if %errorlevel% equ 0 (
    echo   ✅ OK
) else (
    echo   ❌ FALHOU
)

REM Limpeza
del /f /q test_output test_output.exe test_error_output test_error_output.exe >nul 2>&1
del /f /q *_debug.ll >nul 2>&1

REM Resumo final
set /a total_tests=%total_success%+%total_errors%
set /a total_passed=%success_count%+%error_count%

echo.
echo 📊 RESUMO DOS TESTES
echo =================================================
echo Exemplos de sucesso: %success_count%/%total_success%
echo Exemplos de erro: %error_count%/%total_errors%
echo Total: %total_passed%/%total_tests%

if %total_passed% equ %total_tests% (
    echo.
    echo 🎉 TODOS OS TESTES PASSARAM!
    exit /b 0
) else (
    echo.
    echo ⚠️ Alguns testes falharam
    exit /b 1
)