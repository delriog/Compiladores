; ModuleID = "gencode-009.bc"
target triple = "x86_64-unknown-linux-gnu"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"

declare void @"escrevaInteiro"(i32 %".1") 

declare void @"escrevaFlutuante"(float %".1") 

declare i32 @"leiaInteiro"() 

declare float @"leiaFlutuante"() 

@"A" = common global [10 x i32] zeroinitializer, align 4
@"B" = common global [10 x i32] zeroinitializer, align 4
@"C" = common global [10 x i32] zeroinitializer, align 4
define void @"somaVetores"(i32 %"n") 
{
entry:
  %"i" = alloca i32, align 4
  %"expression" = add i32 0, 0
  store i32 %"expression", i32* %"i"
  %"var_comper" = alloca i32
  br label %"loop"
loop:
  %".5" = load i32, i32* %"i"
  %"C_i" = getelementptr [10 x i32], [10 x i32]* @"C", i32 0, i32 %".5"
  %".6" = load i32, i32* %"i"
  %"A[i]" = getelementptr [10 x i32], [10 x i32]* @"A", i32 0, i32 %".6"
  %".7" = load i32, i32* %"A[i]", align 4
  %"expression.1" = add i32 0, %".7"
  %".8" = load i32, i32* %"i"
  %"B[i]" = getelementptr [10 x i32], [10 x i32]* @"B", i32 0, i32 %".8"
  %".9" = load i32, i32* %"B[i]", align 4
  %"expression.2" = add i32 %"expression.1", %".9"
  store i32 %"expression.2", i32* %"C_i"
  %".11" = load i32, i32* %"i"
  %"expression.3" = add i32 0, %".11"
  %"expression.4" = add i32 %"expression.3", 1
  store i32 %"expression.4", i32* %"i"
  br label %"loop_val"
loop_val:
  %".14" = load i32, i32* %"i"
  %"expression.5" = icmp eq i32 %".14", %"n"
  br i1 %"expression.5", label %"loop_end", label %"loop"
loop_end:
  br label %"exit"
exit:
  ret void
}

define i32 @"main"() 
{
entry:
  %"i" = alloca i32, align 4
  %"expression" = add i32 0, 0
  store i32 %"expression", i32* %"i"
  %"var_comper" = alloca i32
  store i32 10, i32* %"var_comper"
  br label %"loop"
loop:
  %".5" = load i32, i32* %"i"
  %"A_i" = getelementptr [10 x i32], [10 x i32]* @"A", i32 0, i32 %".5"
  %"expression.1" = add i32 0, 1
  store i32 %"expression.1", i32* %"A_i"
  %".7" = load i32, i32* %"i"
  %"B_i" = getelementptr [10 x i32], [10 x i32]* @"B", i32 0, i32 %".7"
  %"expression.2" = add i32 0, 1
  store i32 %"expression.2", i32* %"B_i"
  %".9" = load i32, i32* %"i"
  %"expression.3" = add i32 0, %".9"
  %"expression.4" = add i32 %"expression.3", 1
  store i32 %"expression.4", i32* %"i"
  br label %"loop_val"
loop_val:
  %".12" = load i32, i32* %"i"
  %".13" = load i32, i32* %"var_comper"
  %"expression.5" = icmp eq i32 %".12", %".13"
  br i1 %"expression.5", label %"loop_end", label %"loop"
loop_end:
  call void @"somaVetores"(i32 10)
  %"expression.6" = add i32 0, 0
  store i32 %"expression.6", i32* %"i"
  %"var_comper.1" = alloca i32
  store i32 10, i32* %"var_comper.1"
  br label %"loop.1"
loop.1:
  %".19" = load i32, i32* %"i"
  %"C[i]" = getelementptr [10 x i32], [10 x i32]* @"C", i32 0, i32 %".19"
  %".20" = load i32, i32* %"C[i]", align 4
  call void @"escrevaInteiro"(i32 %".20")
  %".22" = load i32, i32* %"i"
  %"expression.7" = add i32 0, %".22"
  %"expression.8" = add i32 %"expression.7", 1
  store i32 %"expression.8", i32* %"i"
  br label %"loop_val.1"
loop_val.1:
  %".25" = load i32, i32* %"i"
  %".26" = load i32, i32* %"var_comper.1"
  %"expression.9" = icmp eq i32 %".25", %".26"
  br i1 %"expression.9", label %"loop_end.1", label %"loop.1"
loop_end.1:
  br label %"exit"
exit:
  ret i32 0
}
