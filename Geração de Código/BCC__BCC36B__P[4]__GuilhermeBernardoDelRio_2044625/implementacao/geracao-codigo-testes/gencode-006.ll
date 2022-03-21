; ModuleID = "gencode-006.bc"
target triple = "x86_64-unknown-linux-gnu"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"

declare void @"escrevaInteiro"(i32 %".1") 

declare void @"escrevaFlutuante"(float %".1") 

declare i32 @"leiaInteiro"() 

declare float @"leiaFlutuante"() 

define i32 @"soma"(i32 %"a", i32 %"b") 
{
entry:
  br label %"exit"
exit:
  %".5" = add i32 %"a", %"b"
  ret i32 %".5"
}

define i32 @"main"() 
{
entry:
  %"a" = alloca i32, align 4
  %"b" = alloca i32, align 4
  %"c" = alloca i32, align 4
  %"i" = alloca i32, align 4
  %"expression" = add i32 0, 0
  store i32 %"expression", i32* %"i"
  %"var_comper" = alloca i32
  store i32 5, i32* %"var_comper"
  br label %"loop"
loop:
  %".5" = call i32 @"leiaInteiro"()
  store i32 %".5", i32* %"a", align 4
  %".7" = call i32 @"leiaInteiro"()
  store i32 %".7", i32* %"b", align 4
  %".9" = load i32, i32* %"a"
  %".10" = load i32, i32* %"b"
  %".11" = call i32 @"soma"(i32 %".9", i32 %".10")
  %"expression.1" = add i32 0, %".11"
  store i32 %"expression.1", i32* %"c"
  %".13" = load i32, i32* %"c"
  call void @"escrevaInteiro"(i32 %".13")
  %".15" = load i32, i32* %"i"
  %"expression.2" = add i32 0, %".15"
  %"expression.3" = add i32 %"expression.2", 1
  store i32 %"expression.3", i32* %"i"
  br label %"loop_val"
loop_val:
  %".18" = load i32, i32* %"i"
  %".19" = load i32, i32* %"var_comper"
  %"expression.4" = icmp eq i32 %".18", %".19"
  br i1 %"expression.4", label %"loop_end", label %"loop"
loop_end:
  br label %"exit"
exit:
  ret i32 0
}
