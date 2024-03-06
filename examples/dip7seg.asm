;program using plugdip7seg
main:
in 72h
out 67h
call sleep
jmp main

sleep:
mvi a, 0
mvi b, 255
l1:
mvi c, 255
l2:
dcr c
cmp c
jnz l2
dcr b
cmp b
jnz l1
ret