CREATE OR REPLACE FUNCTION "data"."fill_report"(p_parcela int8)
  RETURNS "pg_catalog"."varchar" AS $BODY$

DECLARE
	r_par record;
	r_sec record;
	r_cla record;
	r_cat record;
	r_alc record;
	r_qua record;
	v_sql varchar;
	v_sector varchar;
	v_out varchar;
	max_id int8;

BEGIN

	-- Afegim al paràmetre de sistema search_path tots els esquemes
	SET search_path TO cadastre, carto, data, planejament_urba, public;

	-- Creació taula de report
	--PERFORM create_report();

	-- Borrem contingut previ de les taules de report
	DELETE FROM rpt_parcela;
	DELETE FROM rpt_planejament;

	-- Obtenim àrea i refcat
	SELECT ST_Area(geom) AS area, refcat, geom INTO r_par FROM parcela WHERE ninterno = p_parcela;
	
	-- Obtenim sector a través intersecció de les dues capes
	SELECT sectors.codi, sectors.codi||' - '||sectors.descripcio AS descripcio, ST_Area(ST_Intersection(parcela.geom, sectors.geom)) AS area_int
	INTO r_sec
	FROM parcela, sectors_urbanistics AS sectors
	WHERE parcela.ninterno = p_parcela
		AND ST_Intersects(parcela.geom, sectors.geom)
	ORDER BY area_int DESC
	LIMIT 1;

	-- Obtenim classificació del sòl a través intersecció de les dues capes
	SELECT classificacio.codi, classificacio.codi||' - '||classificacio.descripcio AS descripcio, ST_Area(ST_Intersection(parcela.geom, classificacio.geom)) AS area_int
	INTO r_cla
	FROM parcela, classificacio
	WHERE parcela.ninterno = p_parcela
		AND ST_Intersects(parcela.geom, classificacio.geom)
	ORDER BY area_int DESC
	LIMIT 1;

	-- Obtenim adreça
	SELECT tipo_via, nombre_via, primer_numero_policia
	INTO r_cat
	FROM cat_11 INNER JOIN parcela ON cat_11.parcela_catastral = parcela.refcat
	WHERE parcela.ninterno = p_parcela;

	-- Omplim taula de report principal
	v_sql:= 'INSERT INTO rpt_parcela (par_ninterno, par_refcat, par_area, sec_codi, sec_descripcio, cla_codi, cla_descripcio, 
		cat_tipo_via, cat_nombre_via, cat_primer_numero_policia
		) VALUES 
		('||p_parcela||', '||quote_nullable(r_par.refcat)||', '||r_par.area||', '||quote_nullable(r_sec.codi)||', '||quote_nullable(r_sec.descripcio)||', 
		'||quote_nullable(r_cla.codi)||', '||quote_nullable(r_cla.descripcio)||', '||quote_nullable(r_cat.tipo_via)||', '||quote_nullable(r_cat.nombre_via)||', '||quote_nullable(r_cat.primer_numero_policia)||')';
	EXECUTE v_sql;

	-- Actualitzar geometria
	v_sql:= 'UPDATE rpt_parcela
		SET par_geom = parcela.geom
		FROM parcela
		WHERE parcela.ninterno = '||p_parcela;
	EXECUTE v_sql;

	-- Obtenim alçades reguladores a través intersecció de les dues capes
	FOR r_alc IN
		SELECT alc.alcada, alc.area, ST_Area(ST_Intersection(parcela.geom, alc.geom)) AS area_int
		FROM parcela, alcades_reguladores AS alc
		WHERE parcela.ninterno = p_parcela
			AND ST_Intersects(parcela.geom, alc.geom)
		ORDER BY alc.alcada
	LOOP
		v_sql:= 'UPDATE rpt_parcela SET alc_'||r_alc.alcada||' = '||r_alc.area_int||' WHERE par_ninterno = '||p_parcela;
		EXECUTE v_sql;        
	END LOOP;

    -- Calculem àrea de les alçades no definides
	v_sql:= 'UPDATE rpt_parcela SET alc_res = par_area - (COALESCE(alc_0p, 0) + COALESCE(alc_1p, 0) + COALESCE(alc_2p, 0) + COALESCE(alc_3p, 0) + COALESCE(alc_4p, 0) + COALESCE(alc_5p, 0))';
	EXECUTE v_sql;

	-- Obtenim dades de les N qualificacions a través intersecció de les dues capes
	-- Join amb: qualificacio_general, tipus_ordenacio, usos, condicions_edif, condicions_parce
	FOR r_qua IN
		SELECT qua.codi, qua.descripcio, qg.tipus_qualif AS tipus, qg.subzona, qg.definicio, tord.cod_ord AS tord_codi, tord.tipus_ord AS tord_descripcio,
			qua.geom AS qua_geom, ST_Intersection(parcela.geom, qua.geom) AS geom_int, ST_Area(ST_Intersection(parcela.geom, qua.geom)) AS area_int,
			hab_unifamiliar, hab_plurifamiliar, hab_rural, res_especial, res_mobil, hoteler, com_petit, com_mitja, com_gran,
			oficines_serveis, restauracio, recreatiu, magatzem, industrial_1, industrial_2, industrial_3, industrial_4, industrial_5,
			taller_reparacio, educatiu, sanitari, assistencial, cultural, associatiu, esportiu, serveis_publics, serveis_tecnics,
			serveis_ambientals, serveis_radio, aparcament, estacions_servei, agricola, ramader, forestal, lleure, ecologic,
			fondaria_edif, edificabilitat, ocupacio, densitat_hab, vol_max_edif, fondaria_edif_pb, pb, alcada, punt_aplic, sep_min, 
			constr_aux_alcada, constr_auxo_cupacio, tanques, nplantes, alcada_lliure, entresol_pb, sotacoberta, pendent,
			terrasses, elem_sort, cossos_sort, cossos_annexes, porxos, tract_facana, comp_facana, prop_obertura, material_facana,
			material_coberta, fusteria, espai_lliure, altell, altres, front_min, parce_min, prof_min
		FROM parcela, qualificacions AS qua
			INNER JOIN data.qualificacio_general AS qg ON qua.codi = qg.id
			LEFT JOIN data.tipus_ordenacio AS tord ON qg.cod_ord = tord.cod_ord
			LEFT JOIN data.usos ON qg.id = usos.id
			LEFT JOIN data.condicions_edif ON qg.id = condicions_edif.id
			LEFT JOIN data.condicions_parce ON qg.id = data.condicions_parce.id
		WHERE parcela.ninterno = p_parcela
			AND ST_Intersects(parcela.geom, qua.geom)
		ORDER BY area_int DESC
	LOOP
		v_sql:= 'INSERT INTO rpt_planejament (qua_codi, qua_descripcio, area_int, qg_tipus, qg_subzona, qg_definicio, 
			sec_codi, sec_descripcio, cla_codi, cla_descripcio, tord_codi, tord_descripcio, 
			hab_unifamiliar, hab_plurifamiliar, hab_rural, res_especial, res_mobil, hoteler, com_petit, com_mitja, com_gran,
			oficines_serveis, restauracio, recreatiu, magatzem, industrial_1, industrial_2, industrial_3, industrial_4, industrial_5,
			taller_reparacio, educatiu, sanitari, assistencial, cultural, associatiu, esportiu, serveis_publics, serveis_tecnics,
			serveis_ambientals, serveis_radio, aparcament, estacions_servei, agricola, ramader, forestal, lleure, ecologic,
			fondaria_edif, edificabilitat, ocupacio, densitat_hab, vol_max_edif, fondaria_edif_pb, pb, alcada, punt_aplic, sep_min, 
			constr_aux_alcada, constr_auxo_cupacio, tanques, nplantes, alcada_lliure, entresol_pb, sotacoberta, pendent,
			terrasses, elem_sort, cossos_sort, cossos_annexes, porxos, tract_facana, comp_facana, prop_obertura, material_facana,
			material_coberta, fusteria, espai_lliure, altell, altres, front_min, parce_min, prof_min
			) VALUES 
			('||quote_nullable(r_qua.codi)||', '||quote_nullable(r_qua.descripcio)||', '||r_qua.area_int||', '||quote_nullable(r_qua.tipus)||', '||quote_nullable(r_qua.subzona)||', 
			'||quote_nullable(r_qua.definicio)||', '||quote_nullable(r_sec.codi)||', '||quote_nullable(r_sec.descripcio)||', '||quote_nullable(r_cla.codi)||', '||quote_nullable(r_cla.descripcio)||',
			'||quote_nullable(r_qua.tord_codi)||', '||quote_nullable(r_qua.tord_descripcio)||', '||quote_nullable(r_qua.hab_unifamiliar)||', '||quote_nullable(r_qua.hab_plurifamiliar)||', '||quote_nullable(r_qua.hab_rural)||',
			'||quote_nullable(r_qua.res_especial)||', '||quote_nullable(r_qua.res_mobil)||', '||quote_nullable(r_qua.hoteler)||', '||quote_nullable(r_qua.com_petit)||', '||quote_nullable(r_qua.com_mitja)||',
			'||quote_nullable(r_qua.com_gran)||', '||quote_nullable(r_qua.oficines_serveis)||', '||quote_nullable(r_qua.restauracio)||', '||quote_nullable(r_qua.recreatiu)||', '||quote_nullable(r_qua.magatzem)||',
			'||quote_nullable(r_qua.industrial_1)||', '||quote_nullable(r_qua.industrial_2)||', '||quote_nullable(r_qua.industrial_3)||', '||quote_nullable(r_qua.industrial_4)||', '||quote_nullable(r_qua.industrial_5)||',
			'||quote_nullable(r_qua.taller_reparacio)||', '||quote_nullable(r_qua.educatiu)||', '||quote_nullable(r_qua.sanitari)||', '||quote_nullable(r_qua.assistencial)||', '||quote_nullable(r_qua.cultural)||',
			'||quote_nullable(r_qua.associatiu)||', '||quote_nullable(r_qua.esportiu)||', '||quote_nullable(r_qua.serveis_publics)||', '||quote_nullable(r_qua.serveis_tecnics)||', '||quote_nullable(r_qua.serveis_ambientals)||',
			'||quote_nullable(r_qua.serveis_radio)||', '||quote_nullable(r_qua.aparcament)||', '||quote_nullable(r_qua.estacions_servei)||', '||quote_nullable(r_qua.agricola)||', '||quote_nullable(r_qua.ramader)||',
			'||quote_nullable(r_qua.forestal)||', '||quote_nullable(r_qua.lleure)||', '||quote_nullable(r_qua.ecologic)||',
			'||quote_nullable(r_qua.fondaria_edif)||', '||quote_nullable(r_qua.edificabilitat)||', '||quote_nullable(r_qua.ocupacio)||', '||quote_nullable(r_qua.densitat_hab)||', '||quote_nullable(r_qua.vol_max_edif)||',
			'||quote_nullable(r_qua.fondaria_edif_pb)||', '||quote_nullable(r_qua.pb)||', '||quote_nullable(r_qua.alcada)||', '||quote_nullable(r_qua.punt_aplic)||', '||quote_nullable(r_qua.sep_min)||',
			'||quote_nullable(r_qua.constr_aux_alcada)||', '||quote_nullable(r_qua.constr_auxo_cupacio)||', '||quote_nullable(r_qua.tanques)||', '||quote_nullable(r_qua.nplantes)||', '||quote_nullable(r_qua.alcada_lliure)||',
			'||quote_nullable(r_qua.entresol_pb)||', '||quote_nullable(r_qua.sotacoberta)||', '||quote_nullable(r_qua.pendent)||', '||quote_nullable(r_qua.terrasses)||', '||quote_nullable(r_qua.elem_sort)||',
			'||quote_nullable(r_qua.cossos_sort)||', '||quote_nullable(r_qua.cossos_annexes)||', '||quote_nullable(r_qua.porxos)||', '||quote_nullable(r_qua.tract_facana)||', '||quote_nullable(r_qua.comp_facana)||',
			'||quote_nullable(r_qua.prop_obertura)||', '||quote_nullable(r_qua.material_facana)||', '||quote_nullable(r_qua.material_coberta)||', '||quote_nullable(r_qua.fusteria)||', '||quote_nullable(r_qua.espai_lliure)||',
			'||quote_nullable(r_qua.altell)||', '||quote_nullable(r_qua.altres)||', '||quote_nullable(r_qua.front_min)||', '||quote_nullable(r_qua.parce_min)||', '||quote_nullable(r_qua.prof_min)||')';
		--RAISE NOTICE 'sql: %', v_sql;
		EXECUTE v_sql;

		-- Obtenim id del darrer registre insertat
		SELECT MAX(id) INTO max_id FROM rpt_planejament;

		-- Actualitzar geometria i percentatge d'àrea intersectada respecte de la parcela
		UPDATE rpt_planejament 
		SET qua_geom = r_qua.geom_int,
				per_int = (area_int / r_par.area) * 100
		WHERE id = max_id;

	END LOOP;

	-- Eliminem registres que tinguin un percentatge d'intersecció inferior al 5%
	DELETE FROM rpt_planejament WHERE per_int < 5;

	RETURN v_out;

END;
 
$BODY$
  LANGUAGE 'plpgsql' VOLATILE COST 100;

ALTER FUNCTION "data"."fill_report"(p_parcela int8) OWNER TO "gisadmin";