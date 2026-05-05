CREATE OR REPLACE FUNCTION rentu_rokning(kontotypa IN VARCHAR2, p_konto_id IN VARCHAR2, dato_start IN DATE, dato_end IN DATE)
RETURN NUMBER
IS
    saldo NUMBER(12,2);
    last_dato DATE;
    max_dato DATE;
    dato_current DATE;
    end_of_month DATE;
    renta NUMBER;
    samla_renta NUMBER;
    debit_renta NUMBER;
    credit_renta NUMBER;
    max_trans_id NUMBER;
BEGIN

SELECT credit_renta INTO credit_renta 
FROM kontoslag
WHERE kontotypa = kontoslag.kontoslag_id;

SELECT debit_renta INTO debit_renta 
FROM kontoslag
WHERE kontotypa = kontoslag.kontoslag_id;

     samla_renta := 0;
    
    SELECT MAX(log_dato) INTO max_dato
    FROM loggur
    WHERE p_konto_id = loggur.konto_id AND log_dato <= dato_start;

-- makes sure we get the latest transaction in the case where we have duplicate dates.
    SELECT MAX(log_id) INTO max_trans_id
    FROM loggur
    WHERE p_konto_id = loggur.konto_id AND log_dato = max_dato;


-- loys trupuleikan um eingin bóking er. kanska ger eina 0 bóking tá kontoin er stovna.
    SELECT leypandi_saldo INTO saldo
    FROM loggur
    WHERE p_konto_id = loggur.konto_id AND log_dato = max_dato AND max_trans_id = loggur.log_id;
    
    SELECT last_day(dato_start) INTO end_of_month FROM dual;
    dato_current := dato_start;

    LOOP
    IF saldo < 0 THEN
        renta := credit_renta/364.25;
    ELSE
        renta := debit_renta/364.25;
    END IF;
    samla_renta :=  samla_renta + saldo*renta;
       
   
    SELECT MAX(log_id) INTO max_trans_id
    FROM loggur
    WHERE p_konto_id = loggur.konto_id AND log_dato >= dato_current AND log_dato < dato_current + 1;

    IF max_trans_id IS NOT NULL THEN
        SELECT leypandi_saldo INTO saldo
        FROM loggur
        WHERE p_konto_id = loggur.konto_id AND max_trans_id = loggur.log_id;
    END IF;


    IF dato_current = end_of_month THEN
        saldo := saldo +  samla_renta;
         samla_renta := 0;
        SELECT last_day(add_months(dato_current, 1)) INTO end_of_month FROM dual;
    END IF;
         
    EXIT WHEN dato_current >= dato_end;
    SELECT dato_current + 1 INTO dato_current FROM dual;
    END LOOP;
RETURN saldo;
END;
/

CREATE OR REPLACE PROCEDURE rentu_rokning_allar_konti(dato_start IN DATE, dato_end IN DATE)
IS
    rentu_saldo NUMBER;
    bankaboks VARCHAR2(11);
BEGIN
    bankaboks := '69690000016';
    FOR rec IN (
        SELECT konto_id, kontotypa, saldo
        FROM konto
    ) LOOP
        SELECT rentu_rokning(rec.kontotypa, rec.konto_id, dato_start, dato_end) INTO rentu_saldo FROM dual;
        
        INSERT INTO loggur (konto_id, saldo_broyting, móttakari_id)
        VALUES (rec.konto_id, rentu_saldo - rec.saldo, bankaboks);
        
        INSERT INTO loggur (konto_id, saldo_broyting, móttakari_id)
        VALUES (bankaboks, -(rentu_saldo - rec.saldo), rec.konto_id);
        
    END LOOP;
END;
/
