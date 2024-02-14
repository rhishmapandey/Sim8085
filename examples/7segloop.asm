;program using plugsingle7seg
call ld_act_tomem
mvi a, 00h
l1:
call disp
call secdelay
inr a
cpi 10h
jnz l1
mvi a, 00h
jmp l1
hlt

;update the 7segment display
updisp:
out 67h
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
inx h
mvi m, 6fh
inx h
mvi m, 77h
inx h
mvi m, 7ch
inx h
mvi m, 39h
inx h
mvi m, 5eh
inx h
mvi m, 79h
inx h
mvi m, 71h
inx h
lxi h, 0000h
ret

;get the mem by offset of a and sends to 7seg
disp:
push psw
push h
mvi h, 00h
mov l, a
mov a, m
call updisp
pop h
pop psw
ret

