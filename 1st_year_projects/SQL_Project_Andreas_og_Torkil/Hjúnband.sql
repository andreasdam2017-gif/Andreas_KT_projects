CREATE OR REPLACE PROCEDURE nýggj_hjún (
    p1_p_id IN NUMBER,
    p2_p_id IN NUMBER
) IS
    p1_id        NUMBER;
    p2_id        NUMBER;
    person_count NUMBER;
    active_count NUMBER;
BEGIN
    IF p1_p_id IS NULL OR p2_p_id IS NULL THEN
        RAISE_APPLICATION_ERROR(-20000, 'Báðir persónar mugu veljast.');
    END IF;

    IF p1_p_id = p2_p_id THEN
        RAISE_APPLICATION_ERROR(-20001, 'Ein persónur kann ikki giftast við sær sjálvum.');
    END IF;

    p1_id := LEAST(p1_p_id, p2_p_id);
    p2_id := GREATEST(p1_p_id, p2_p_id);

    SELECT COUNT(*)
      INTO person_count
      FROM pers
     WHERE p_id IN (p1_id, p2_id);

    IF person_count <> 2 THEN
        RAISE_APPLICATION_ERROR(-20004, 'Ein av persónunum er ikki til.');
    END IF;

    SELECT COUNT(*)
      INTO active_count
      FROM hjúnaband
     WHERE skild_dato IS NULL
       AND (p1_id IN (p1_id, p2_id) OR p2_id IN (p1_id, p2_id));

    IF active_count > 0 THEN
        RAISE_APPLICATION_ERROR(-20002, 'Ein av persónunum er longu í virknu hjúnabandi.');
    END IF;

    INSERT INTO hjúnaband (p1_id, p2_id, gift_dato, skild_dato)
    VALUES (p1_id, p2_id, SYSDATE, NULL);
END nýggj_hjún;
/

CREATE OR REPLACE PROCEDURE end_hjún (
    p1_p_id IN NUMBER,
    p2_p_id IN NUMBER
) IS
    p1_id        NUMBER;
    p2_id        NUMBER;
    person_count NUMBER;
BEGIN
    IF p1_p_id IS NULL OR p2_p_id IS NULL THEN
        RAISE_APPLICATION_ERROR(-20000, 'Báðir persónar mugu veljast.');
    END IF;

    IF p1_p_id = p2_p_id THEN
        RAISE_APPLICATION_ERROR(-20001, 'Ein persónur kann ikki skiljast frá sær sjálvum.');
    END IF;

    p1_id := LEAST(p1_p_id, p2_p_id);
    p2_id := GREATEST(p1_p_id, p2_p_id);

    SELECT COUNT(*)
      INTO person_count
      FROM pers
     WHERE p_id IN (p1_id, p2_id);

    IF person_count <> 2 THEN
        RAISE_APPLICATION_ERROR(-20004, 'Ein av persónunum er ikki til.');
    END IF;

    UPDATE hjúnaband
       SET skild_dato = SYSDATE
     WHERE skild_dato IS NULL
       AND p1_id = p1_id
       AND p2_id = p2_id;

    IF SQL%ROWCOUNT = 0 THEN
        RAISE_APPLICATION_ERROR(-20005, 'Einki virkið hjúnaband funnið hjá hesum báðum.');
    END IF;
END end_hjún;
/
