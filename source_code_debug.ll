; ModuleID = "main"
target triple = "unknown-unknown-unknown"
target datalayout = ""

declare i32 @"printf"(i8* %".1", ...)

declare i32 @"puts"(i8* %".1")

define i32 @"main"()
{
entry:
  %"resultado" = alloca double
  store double 0x4018000000000000, double* %"resultado"
  %"i" = alloca double
  store double              0x0, double* %"i"
  br label %"for_cond_1"
for_cond_1:
  %"i.1" = load double, double* %"i"
  %"cmptmp" = fcmp ult double %"i.1", 0x4008000000000000
  br i1 %"cmptmp", label %"for_body_1", label %"for_end_1"
for_body_1:
  %".6" = getelementptr [1 x i8], [1 x i8]* @".str.340095", i32 0, i32 0
  %".7" = call i32 @"puts"(i8* %".6")
  br label %"for_inc_1"
for_inc_1:
  %"i.2" = load double, double* %"i"
  %"addtmp" = fadd double %"i.2", 0x3ff0000000000000
  br label %"for_cond_1"
for_end_1:
  ret i32 0
}

@".str.340095" = private constant [1 x i8] c"\00"