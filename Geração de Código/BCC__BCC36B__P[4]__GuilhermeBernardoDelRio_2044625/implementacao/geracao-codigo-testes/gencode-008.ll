; ModuleID = "gencode-008.bc"
target triple = "x86_64-unknown-linux-gnu"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"

declare void @"escrevaInteiro"(i32 %".1") 

declare void @"escrevaFlutuante"(float %".1") 

declare i32 @"leiaInteiro"() 

declare float @"leiaFlutuante"() 

@"A" = common global [1024 x i32] zeroinitializer, align 4
@"B" = common global [1024 x i32] zeroinitializer, align 4
define i32 @"main"() 
{
entry:
  %"a" = alloca i32, align 4
  %"i" = alloca i32, align 4
  %"expression" = add i32 0, 0
  store i32 %"expression", i32* %"i"
  %"var_comper" = alloca i32
  store i32 1024, i32* %"var_comper"
  br label %"loop"
loop:
  %".5" = call i32 @"leiaInteiro"()
  store i32 %".5", i32* %"a", align 4
  %".7" = load i32, i32* %"i"
  %"A_i" = getelementptr [1024 x i32], [1024 x i32]* @"A", i32 0, i32 %".7"
  %".8" = load i32, i32* %"a"
  %"expression.1" = add i32 0, %".8"
  store i32 %"expression.1", i32* %"A_i"
  %".10" = load i32, i32* %"i"
  %"expression.2" = add i32 0, %".10"
  %"expression.3" = add i32 %"expression.2", 1
  store i32 %"expression.3", i32* %"i"
  br label %"loop_val"
loop_val:
  %".13" = load i32, i32* %"i"
  %".14" = load i32, i32* %"var_comper"
  %"expression.4" = icmp eq i32 %".13", %".14"
  br i1 %"expression.4", label %"loop_end", label %"loop"
loop_end:
  %"expression.5" = add i32 0, 0
  store i32 %"expression.5", i32* %"i"
  %"var_comper.1" = alloca i32
  store i32 1024, i32* %"var_comper.1"
  br label %"loop.1"
loop.1:
  %".19" = load i32, i32* %"i"
  %"B_1023-i" = sub i32 1023, %".19"
  %"B_1023-i.1" = getelementptr [1024 x i32], [1024 x i32]* @"B", i32 0, i32 %"B_1023-i"
  %".20" = load i32, i32* %"i"
  %"A[i]" = getelementptr [1024 x i32], [1024 x i32]* @"A", i32 0, i32 %".20"
  %".21" = load i32, i32* %"A[i]", align 4
  %"expression.6" = add i32 0, %".21"
  store i32 %"expression.6", i32* %"B_1023-i.1"
  %".23" = load i32, i32* %"i"
  %"expression.7" = add i32 0, %".23"
  %"expression.8" = add i32 %"expression.7", 1
  store i32 %"expression.8", i32* %"i"
  br label %"loop_val.1"
loop_val.1:
  %".26" = load i32, i32* %"i"
  %".27" = load i32, i32* %"var_comper.1"
  %"expression.9" = icmp eq i32 %".26", %".27"
  br i1 %"expression.9", label %"loop_end.1", label %"loop.1"
loop_end.1:
  %"expression.10" = add i32 0, 0
  store i32 %"expression.10", i32* %"i"
  %"var_comper.2" = alloca i32
  store i32 1024, i32* %"var_comper.2"
  br label %"loop.2"
loop.2:
  %".32" = load i32, i32* %"i"
  %"B[i]" = getelementptr [1024 x i32], [1024 x i32]* @"B", i32 0, i32 %".32"
  %".33" = load i32, i32* %"B[i]", align 4
  call void @"escrevaInteiro"(i32 %".33")
  %".35" = load i32, i32* %"i"
  %"expression.11" = add i32 0, %".35"
  %"expression.12" = add i32 %"expression.11", 1
  store i32 %"expression.12", i32* %"i"
  br label %"loop_val.2"
loop_val.2:
  %".38" = load i32, i32* %"i"
  %".39" = load i32, i32* %"var_comper.2"
  %"expression.13" = icmp eq i32 %".38", %".39"
  br i1 %"expression.13", label %"loop_end.2", label %"loop.2"
loop_end.2:
  br label %"exit"
exit:
  ret i32 0
}
