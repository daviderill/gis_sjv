CREATE OR REPLACE FUNCTION "data"."test_function"(p_parcela int8)
  RETURNS "pg_catalog"."varchar" AS $BODY$

DECLARE
	v_refcat varchar;

BEGIN

	SELECT refcat INTO v_refcat FROM carto.parcela WHERE ninterno = p_parcela;
	RETURN v_refcat;

END;
 
$BODY$
  LANGUAGE 'plpgsql' VOLATILE COST 100
;

ALTER FUNCTION "data"."test_function"(p_parcela int8) OWNER TO "gisadmin";