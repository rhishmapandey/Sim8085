;program using plugsingle7seg
call ld_act_tomem
call getval
call calcbitsum 
call disp
jmp 0800h
hlt

getval:
in 72h
ret

;update the 7segment display
updisp:
out 67h
ret

ld_act_tomem:
lxi h, 0000h
mvi m, 3fh
inx h
mvi m, 06h
inx h
mvi m, 5bh
inx h
mvi m, 4fh
inx h
mvi m, 66h
inx h
mvi m, 6dh
inx h
mvi m, 7dh
inx h
mvi m, 07h
inx h
mvi m, 7fh
lxi h, 0000h
ret

;get the mem by offset of a and sends to 7seg
disp:
cpi 09h
jnc dispskip
push psw
push h
mvi h, 00h
mov l, a
mov a, m
call updisp
pop h
pop psw
dispskip:
ret


calcbitsum:
mvi b, 00h
mvi c, 00h
cl1:
mov d, a
ani 01h
cpi 00h
jz addskip
inr b
addskip:
mov a, d
rar
inr c
mov d, a
mvi a, 08h
cmp c
mov a, d
jnz cl1
mov a, b
ret 