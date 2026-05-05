CREATE OR REPLACE FUNCTION ptal_gen(føðingardag IN VARCHAR2, kyn IN VARCHAR2)
RETURN VARCHAR2
IS
    summ NUMBER;
    I NUMBER;
    J NUMBER;
    rest NUMBER;
    j_end NUMBER;
    p_count NUMBER;
    new_ptal VARCHAR(9);
    kyn_tal NUMBER;
BEGIN
    IF LENGTH(føðingardag) != 8 THEN
        RETURN '';
    END IF;
    IF kyn = 'm' THEN
        kyn_tal := 1;
    ELSIF kyn = 'k' THEN
        kyn_tal := 0;
    END IF;
    
    IF MOD(TO_NUMBER(substr(føðingardag, 6, 1)),2) = 0 THEN
        J := 5;
        ELSE
        J := 0;
    END IF;
    j_end := J +4;
    I := 0;
    
        LOOP
            LOOP
            
                new_ptal := NULL;
                p_count := NULL;
                
                summ := 
                3*TO_NUMBER(substr(føðingardag, 1, 1)) +
                2*TO_NUMBER(substr(føðingardag, 2, 1)) +
                7*TO_NUMBER(substr(føðingardag, 3, 1)) +
                6*TO_NUMBER(substr(føðingardag, 4, 1)) +
                5*TO_NUMBER(substr(føðingardag, 7, 1)) +
                4*TO_NUMBER(substr(føðingardag, 8, 1)) +
                3*J +
                2*I +
                1*0;
                
                rest :=11- MOD(summ, 11);
                IF rest < 10 AND MOD(rest, 2) = kyn_tal  THEN
                    new_ptal := substr(føðingardag, 1, 4) || substr(føðingardag, 7, 8) || to_char(J) || to_char(I)|| to_char(rest);
                    --return rest;
                    SELECT COUNT(*)
                    INTO p_count
                    FROM pers
                    WHERE p_tal = new_ptal;
                END IF;
                I := I+1;
                EXIT WHEN I > 9 OR (p_count = 0 AND new_ptal IS NOT NULL);
            END LOOP;
            I := 0;
            J := J+1;
            EXIT WHEN J > j_end OR (p_count = 0 AND new_ptal IS NOT NULL);
        END LOOP;
    RETURN new_ptal;
END;