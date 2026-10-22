;------------------------------------------------------------
; ping / pong на двух таймерах
; МК: ATmega8, кварц 16 МГц
; USART: 9600 бод, 8N1
;
; Timer1 и Timer2 оба настроены в CTC и дают прерывание
; раз в 1 мс. В прерываниях крутятся программные счётчики,
; когда счётчик дошёл до нуля - ставим флаг, а строку
; отправляет уже основной цикл (в прерывании ждать UART
; нельзя, он медленный).
;------------------------------------------------------------

.include "m8def.inc"

.equ F_CPU    = 16000000
.equ BAUD     = 9600
.equ UBRR_VAL = F_CPU/(16*BAUD) - 1     ; = 103

; интервалы в миллисекундах, от 1 до 65535
.equ TIMER1_INTERVAL = 1000
.equ TIMER2_INTERVAL = 1500

; 16 МГц / 64 / 250 = 1000 Гц -> тик 1 мс
.equ TICK_OCR = F_CPU/64/1000 - 1       ; = 249

.def temp   = r16
.def sreg_s = r17   ; сюда прерывания сохраняют SREG (они не вложенные, так что одного хватит)
.def cnt1L  = r18   ; счётчик таймера 1
.def cnt1H  = r19
.def cnt2L  = r20   ; счётчик таймера 2
.def cnt2H  = r21
.def flag1  = r22   ; 1 = пора слать TIMER1_STR
.def flag2  = r23   ; 1 = пора слать TIMER2_STR

.cseg
.org 0x000
    rjmp reset
.org OC2addr
    rjmp timer2_isr
.org OC1Aaddr
    rjmp timer1_isr

.org INT_VECTORS_SIZE

reset:
    ; стек
    ldi  temp, high(RAMEND)
    out  SPH, temp
    ldi  temp, low(RAMEND)
    out  SPL, temp

    ; --- USART ---
    ldi  temp, high(UBRR_VAL)
    out  UBRRH, temp
    ldi  temp, low(UBRR_VAL)
    out  UBRRL, temp
    ldi  temp, (1<<TXEN)            ; нужен только передатчик
    out  UCSRB, temp
    ; без URSEL запись уйдёт в UBRRH, у меги8 они на одном адресе
    ldi  temp, (1<<URSEL)|(1<<UCSZ1)|(1<<UCSZ0)
    out  UCSRC, temp

    ; --- счётчики и флаги ---
    ldi  cnt1L, low(TIMER1_INTERVAL)
    ldi  cnt1H, high(TIMER1_INTERVAL)
    ldi  cnt2L, low(TIMER2_INTERVAL)
    ldi  cnt2H, high(TIMER2_INTERVAL)
    clr  flag1
    clr  flag2

    ; --- Timer1: CTC по OCR1A ---
    ldi  temp, high(TICK_OCR)       ; 16-битные регистры: сначала старший байт
    out  OCR1AH, temp
    ldi  temp, low(TICK_OCR)
    out  OCR1AL, temp
    clr  temp
    out  TCNT1H, temp
    out  TCNT1L, temp
    out  TCCR1A, temp

    ; --- Timer2: CTC по OCR2 ---
    ldi  temp, TICK_OCR
    out  OCR2, temp
    clr  temp
    out  TCNT2, temp

    ; разрешаем прерывания по совпадению
    ldi  temp, (1<<OCIE1A)|(1<<OCIE2)
    out  TIMSK, temp

    ; запуск обоих таймеров, делитель 64
    ldi  temp, (1<<WGM12)|(1<<CS11)|(1<<CS10)
    out  TCCR1B, temp
    ldi  temp, (1<<WGM21)|(1<<CS22)          ; у Timer2 /64 это CS22
    out  TCCR2, temp
    ; сброс предделителей, чтобы таймеры стартовали одновременно
    ldi  temp, (1<<PSR10)|(1<<PSR2)
    out  SFIOR, temp

    sei

;------------------------------------------------------------
main:
    tst  flag1
    breq check2
    clr  flag1                      ; сбрасываем до отправки, чтобы не потерять следующее срабатывание
    ldi  ZL, low(TIMER1_STR*2)
    ldi  ZH, high(TIMER1_STR*2)
    rcall uart_puts
check2:
    tst  flag2
    breq main
    clr  flag2
    ldi  ZL, low(TIMER2_STR*2)
    ldi  ZH, high(TIMER2_STR*2)
    rcall uart_puts
    rjmp main

;------------------------------------------------------------
; вывод строки из флеша, адрес в Z, конец строки - 0
uart_puts:
    lpm  temp, Z+
    tst  temp
    breq puts_end
    rcall uart_putc
    rjmp uart_puts
puts_end:
    ret

; отправка байта из temp
uart_putc:
    sbis UCSRA, UDRE                ; ждём пока освободится буфер
    rjmp uart_putc
    out  UDR, temp
    ret

;------------------------------------------------------------
; прерывания, каждое раз в 1 мс
timer1_isr:
    in   sreg_s, SREG
    subi cnt1L, 1
    sbci cnt1H, 0                   ; Z после sbci учитывает оба байта
    brne t1_exit
    ldi  cnt1L, low(TIMER1_INTERVAL)
    ldi  cnt1H, high(TIMER1_INTERVAL)
    ldi  flag1, 1
t1_exit:
    out  SREG, sreg_s
    reti

timer2_isr:
    in   sreg_s, SREG
    subi cnt2L, 1
    sbci cnt2H, 0
    brne t2_exit
    ldi  cnt2L, low(TIMER2_INTERVAL)
    ldi  cnt2H, high(TIMER2_INTERVAL)
    ldi  flag2, 1
t2_exit:
    out  SREG, sreg_s
    reti

;------------------------------------------------------------
; строки (лишний 0 в конце - чтобы длина была чётной)
TIMER1_STR: .db "ping", 13, 10, 0, 0
TIMER2_STR: .db "pong", 13, 10, 0, 0
