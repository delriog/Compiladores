; ModuleID = "gencode-003.bc"
target triple = "x86_64-unknown-linux-gnu"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"

declare void @"escrevaInteiro"(i32 %".1") 

declare void @"escrevaFlutuante"(float %".1") 

declare i32 @"leiaInteiro"() 

declare float @"leiaFlutuante"() 

@"a" = common global i32 0, align 4
define i32 @"main"() 
{
entry:
  %"ret" = alloca i32, align 4
  %"expression" = add i32 0, 25
  store i32 %"expression", i32* @"a"
  %"var_comper_right" = alloca i32
  %"var_comper_left" = alloca i32
  store i32 5, i32* %"var_comper_right"
  %"if_test" = icmp sgt i32* @"a", %"var_comper_right"
  br i1 %"if_test", label %"iftrue", label %"iffalse"
iftrue:
  %"var_comper_right.1" = alloca i32
  %"var_comper_left.1" = alloca i32
  store i32 20, i32* %"var_comper_right.1"
  %"if_test.1" = icmp slt i32* @"a", %"var_comper_right.1"
  br i1 %"if_test.1", label %"iftrue.1", label %"iffalse.1"
iffalse:
  %"expression.3" = add i32 0, 0
  store i32 %"expression.3", i32* %"ret"
  br label %"ifend"
ifend:
  br label %"exit"
iftrue.1:
  %"expression.1" = add i32 0, 1
  store i32 %"expression.1", i32* %"ret"
  br label %"ifend.1"
iffalse.1:
  %"expression.2" = add i32 0, 2
  store i32 %"expression.2", i32* %"ret"
  br label %"ifend.1"
ifend.1:
  br label %"ifend"
exit:
  %".15" = load i32, i32* %"ret"
  ret i32 %".15"
}
