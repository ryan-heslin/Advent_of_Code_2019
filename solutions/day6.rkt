#lang racket
;;satellite -> parent
;; For each satellite except root
;; traverse(satellite)
;; parent = map[satellite]
;; Start traverse from each key
;; Memoize each satellite's distance from center

(define (split str)
  (let ([parts (string-split str ")")])
    (cons (car(cdr parts)) (car parts))))

(define (parse lines)
  (let ([pairs (map split lines)])
    (make-immutable-hash pairs)
    )
  )

(define (solve-part1 graph root)
  (letrec ([memo (make-hash )]
           [traverse (lambda (satellite)
                       ;;(print (hash-ref graph "HT6"))
                       (cond [(equal? satellite root) 0] ;; At root, so just count orbit
                             [(false? (hash-ref memo satellite #f)) ;;Not yet traversed, so compute
                              (let([result (+ 1 (traverse (hash-ref graph satellite) ))])
                                (hash-set! memo satellite result)
                                result)]
                             [else (hash-ref memo satellite)] ;;Available, so read cache
                             )
                       )]
           )
    (foldl + 0 (map traverse (hash-keys graph)))

    )
  )

(define (solve-part2 graph start dest root)
  (letrec ([memo (make-hash)]
           [traverse (lambda (satellite acc )
                       (hash-set! memo satellite acc)
                       (if (equal? root satellite)
                           acc
                           (traverse (hash-ref graph satellite) (add1 acc))
                           )
                       )]
           [complete (lambda (satellite acc)
                       (let ([res (hash-ref memo satellite #f)])
                         (if (false? res)
                             (complete (hash-ref graph satellite) (add1 acc))
                             (+ acc res) ;;First shared orbit
                             )))])
    (traverse (hash-ref graph start) 0)
    (complete (hash-ref graph dest) 0)
    ))

(define raw-input (file->lines "inputs/day6.txt"))
(define root "COM")
(define orbits (parse raw-input))
(define part1 (solve-part1 orbits root))
(print part1)
(display "\n")
(define part2 (solve-part2 orbits "YOU" "SAN" root))
(print part2)
(display "\n")
