; ModuleID = "gencode-013.bc"
target triple = "x86_64-unknown-linux-gnu"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"

declare void @"escrevaInteiro"(i32 %".1") 

declare void @"escrevaFlutuante"(float %".1") 

declare i32 @"leiaInteiro"() 

declare float @"leiaFlutuante"() 

define i32 @"maiorde2"(i32 %"x", i32 %"y") 
{
entry:
  %"var_comper_right" = alloca i32
  %"var_comper_left" = alloca i32
  store i32 %"x", i32* %"var_comper_left"
  store i32 %"y", i32* %"var_comper_left"
  %"if_test" = icmp sgt i32* %"var_comper_left", %"var_comper_right"
  br i1 %"if_test", label %"iftrue", label %"iffalse"
iftrue:
  br label %"exit"
iffalse:
ifend:
  br label %"exit.1"
exit:
  ret i32 %"x"
exit.1:
  ret i32 %"y"
}

define i32 @"maiorde4"(i32 %"a", i32 %"b", i32 %"c", i32 %"d") 
{
entry:
  br label %"exit"
exit:
}

define i32 @"main"() 
{
entry:
  %"A" = alloca i32, align 4
  %"B" = alloca i32, align 4
  %"C" = alloca i32, align 4
  %"D" = alloca i32, align 4
  %".2" = call i32 @"leiaInteiro"()
  store i32 %".2", i32* %"A", align 4
  %".4" = call i32 @"leiaInteiro"()
  store i32 %".4", i32* %"B", align 4
  %".6" = call i32 @"leiaInteiro"()
  store i32 %".6", i32* %"C", align 4
  %".8" = call i32 @"leiaInteiro"()
  store i32 %".8", i32* %"D", align 4
  br label %"exit"
exit:
  ret i32 0
}
