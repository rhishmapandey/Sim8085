;recursion for fibbonacci
mvi b, 06h
call fibbo
hlt
;see how call stack grows from address 0xffff
;the n in b (index for 0)
;get the ret in c
fibbo:
;check for 0 and 1
push psw
mov a, b
cpi 02h
jc fibo1
push psw
push b
xra a

;fibbo n-1
dcr b
call fibbo
add c

;fibbo n-2
dcr b
call fibbo
add c

mov d, a
pop b
pop psw
mov a, d
fibo1:
mov c, a
pop psw
ret