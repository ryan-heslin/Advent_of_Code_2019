#lang racket

(define (decreasing chrs)
  (let* ([lst (string->list chrs )]
         [sorted (sort lst char<?)])
    (equal? lst sorted )
    )
  )

(define (valid num strict)
  (let ([str (number->string num)])
    (if (and (regexp-match #px".*([0-9])\\1.*" str)
             (decreasing str)
             (or (not strict) (regexp-match #px"(?:(\\d)(?!\\1)|(?<=^))(\\d)\\2(?!\\2)" str)))
        1
        0
        )))

(define (try-numbers cur upper strict)
  (if (> cur upper)
      0
      (+ (valid cur strict)  (try-numbers (+ cur 1)  upper strict)
         )
      ))

(define raw "356261-846303")
(define range (map string->number (regexp-split #rx"-" raw)))
(define part1 (try-numbers (first range) (first (rest range)) #f))
(print part1)
(display "\n")

(define part2 (try-numbers (first range) (first (rest range)) #t))
(print part2)
(display "\n")
