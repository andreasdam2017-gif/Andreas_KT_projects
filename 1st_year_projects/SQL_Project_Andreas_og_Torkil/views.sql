CREATE OR REPLACE VIEW v_foreldur_barn_kontur AS
SELECT
    rel.foreldur_id,
    rel.barn_id,
    k.konto_id,
    k.saldo
FROM (
    SELECT p1_id AS foreldur_id, barn_id
    FROM børn

    UNION ALL

    SELECT p2_id AS foreldur_id, barn_id
    FROM børn
    WHERE p2_id IS NOT NULL
) rel
JOIN pers barn
    ON barn.p_id = rel.barn_id
JOIN kundi ku
    ON ku.p_id = rel.barn_id
JOIN konto k
    ON k.eigari_p_id = ku.kunda_id
WHERE barn.føðingardag IS NOT NULL
  AND ADD_MONTHS(TO_DATE(barn.føðingardag, 'DDMMYYYY'), 12 * 18) > TRUNC(SYSDATE);
/


CREATE OR REPLACE VIEW v_hjunafelaga_kontur AS
SELECT
    rel.brukari_p_id,
    rel.maki_p_id,
    k.konto_id,
    k.saldo
FROM (
    SELECT p1_id AS brukari_p_id, p2_id AS maki_p_id
    FROM hjúnaband
    WHERE skild_dato IS NULL

    UNION ALL

    SELECT p2_id AS brukari_p_id, p1_id AS maki_p_id
    FROM hjúnaband
    WHERE skild_dato IS NULL
) rel
JOIN kundi ku
    ON ku.p_id = rel.maki_p_id
JOIN konto k
    ON k.eigari_p_id = ku.kunda_id;
/
CREATE OR REPLACE VIEW v_kontoavrit AS
SELECT
    l.log_id,
    l.konto_id,
    p.p_id AS eigari_p_id,
    p.fornavn || ' ' || p.eftirnavn AS eigari_navn,
    l.log_dato,
    l.saldo_broyting,
    l.leypandi_saldo,
    l.móttakari_id AS mottakari_konto_id,
    mp.p_id AS mottakari_p_id,
    mp.fornavn || ' ' || mp.eftirnavn AS mottakari_navn,
    l.tekst,
    k.saldo AS nuverandi_saldo
FROM loggur l
JOIN konto k
    ON k.konto_id = l.konto_id
JOIN kundi ku
    ON ku.kunda_id = k.eigari_p_id
JOIN pers p
    ON p.p_id = ku.p_id
LEFT JOIN konto mk
    ON mk.konto_id = l.móttakari_id
LEFT JOIN kundi mku
    ON mku.kunda_id = mk.eigari_p_id
LEFT JOIN pers mp
    ON mp.p_id = mku.p_id;
/
CREATE OR REPLACE VIEW v_kundi_samla_saldo AS
SELECT
    ku.kunda_id,
    ku.p_id,
    COUNT(k.konto_id) AS tal_av_kontum,
    SUM(k.saldo) AS samlað_saldo
FROM kundi ku
LEFT JOIN konto k
    ON k.eigari_p_id = ku.kunda_id
GROUP BY ku.kunda_id, ku.p_id;
/
