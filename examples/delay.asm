call delay
hlt



delay:
push psw
push b
lxi b, ffffh
delay_l1:
mvi b, ffh
delay_l2:
dcr b
mov a, b
cpi 00h
jnz delay_l2
dcr c
mov a, c
cpi 00h
jnz delay_l1
pop b
pop psw
ret