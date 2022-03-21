; ModuleID = "gencode-004.bc"
target triple = "x86_64-unknown-linux-gnu"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"

declare void @"escrevaInteiro"(i32 %".1") 

declare void @"escrevaFlutuante"(float %".1") 

declare i32 @"leiaInteiro"() 

declare float @"leiaFlutuante"() 

@"n" = common global i32 0, align 4
@"soma" = common global i32 0, align 4
define i32 @"main"() 
{
entry:
  %"expression" = add i32 0, 10
  store i32 %"expression", i32* @"n"
  %"expression.1" = add i32 0, 0
  store i32 %"expression.1", i32* @"soma"
  %"var_comper" = alloca i32
  store i32 0, i32* %"var_comper"
  br label %"loop"
loop:
  %".6" = load i32, i32* @"soma"
  %"expression.2" = add i32 0, %".6"
  %".7" = load i32, i32* @"n"
  %"expression.3" = add i32 %"expression.2", %".7"
  store i32 %"expression.3", i32* @"soma"
  %".9" = load i32, i32* @"n"
  %"expression.4" = add i32 0, %".9"
  %"expression.5" = sub i32 %"expression.4", 1
  store i32 %"expression.5", i32* @"n"
  br label %"loop_val"
loop_val:
  %".12" = load i32, i32* @"n"
  %".13" = load i32, i32* %"var_comper"
  %"expression.6" = icmp eq i32 %".12", %".13"
  br i1 %"expression.6", label %"loop_end", label %"loop"
loop_end:
  %".15" = load i32, i32* @"soma"
  call void @"escrevaInteiro"(i32 %".15")
  br label %"exit"
exit:
  ret i32 0
}
