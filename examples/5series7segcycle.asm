;program using plugfive7seg
l1:
call cyclehello
call updateall
call secdelay
jmp l1
hlt

;send update signal
updateall:
push psw
mvi a, 70h
out 67h
pop psw
ret

;halfsecdelay
hsecdelay:
push b
push psw
lxi b, ffffh
hsecdelayloop: 
dcx b
mov a, b
ora c
jnz hsecdelayloop
pop psw
pop b
ret

;sec delay
secdelay:
call hsecdelay
call hsecdelay
ret

;update 7seg
;b contains the disp to sel
;c contains the data to set
up7set:
push psw
push b
push d
;ln
mov a, b
ral
ral
ral
ral
ani 70h
mov b, a
mov a, c
ani 0fh
mov d, a
mov a, c
ani f0h
rar
rar
rar
rar
mov e, a
mov a, b
ora d
out 67h
mov a, b
ora e
ori 80h
out 67h
ral
ral
ral
ral
pop d
pop b
pop psw
ret

cyclehello:
call cylc
mvi c, 76h
call cylc
call up7set
mvi c, 79h
call cylc
call up7set
mvi c, 38h
call cylc
call up7set
mvi c, 38h
call cylc
call up7set
mvi c, bfh
call cylc
call up7set
ret

setallblack:
mvi b, 00h
mvi a, 05h
mov c, b
sab1:
call up7set
inr b
cmp b
jnz sab1
ret

cylc:
push psw
inr b
mov a, b
cpi 05h
jnz cylcj
mvi b, 00h
cylcj:
pop psw
ret
