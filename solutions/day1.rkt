#lang racket
(define (fuel mass)
  (-(floor (/ mass 3)) 2)
  )

(define (fuel-rec mass)
  (let ([res (fuel mass)])
    (if (< res 1)
        0
        (+ res (fuel-rec res))
        )
    )
  )

(define (summer f)
  (letrec
      ([res (lambda (xs) (if (empty? xs )
                             0
                             (+ (f (first xs)) (res (rest xs)))
                             ))
            ])
    res
    )
  )

(define raw-input (file->lines "inputs/day1.txt"))
(define numbers (map string->number raw-input))
(define  fuel-summer (summer fuel) )
(define part-1 (fuel-summer numbers))
(print part-1)
(print "\n")

(define  fuel-rec-summer (summer fuel-rec) )
(define part-2 (fuel-rec-summer numbers))
(print part-2)
