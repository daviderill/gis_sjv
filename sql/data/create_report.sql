CREATE OR REPLACE FUNCTION "data"."create_report"()
  RETURNS "pg_catalog"."void" AS $BODY$

BEGIN

-- Creaci� taules de report
DROP TABLE IF EXISTS "data"."rpt_parcela";
CREATE TABLE "data"."rpt_parcela" (
"par_ninterno" int8,
"par_refcat" varchar(255),
"par_area" numeric(14,4),
"par_adresa" varchar(255),
"par_geom" "public".geometry,
"sec_codi" varchar(10),
"sec_descripcio" varchar(200),
"cla_codi" varchar(10),
"cla_descripcio" varchar(200),
PRIMARY KEY ("par_ninterno") 
);
ALTER TABLE "data"."rpt_parcela" OWNER TO "gisadmin";

DROP TABLE IF EXISTS "data"."rpt_planejament";
CREATE TABLE "data"."rpt_planejament" (
"id" SERIAL,
"qua_codi" varchar(10),
"qua_descripcio" varchar,
"qua_geom" "public".geometry,
"area_int" numeric(14,2), 
"per_int" numeric(5,2),
"qg_tipus" varchar,
"qg_subzona" varchar,
"qg_definicio" varchar,
"sec_codi" varchar(10),
"sec_descripcio" varchar(200),
"cla_codi" varchar(10),
"cla_descripcio" varchar(200),
"tord_codi" varchar,
"tord_descripcio" varchar,
"hab_unifamiliar" varchar,
"hab_plurifamiliar" varchar,
"hab_rural" varchar,
"res_especial" varchar,
"res_mobil" varchar,
"hoteler" varchar,
"com_petit" varchar,
"com_mitja" varchar,
"com_gran" varchar,
"oficines_serveis" varchar,
"restauracio" varchar,
"recreatiu" varchar,
"magatzem" varchar,
"industrial_1" varchar,
"industrial_2" varchar,
"industrial_3" varchar,
"industrial_4" varchar,
"industrial_5" varchar,
"taller_reparacio" varchar,
"educatiu" varchar,
"sanitari" varchar,
"assistencial" varchar,
"cultural" varchar,
"associatiu" varchar,
"esportiu" varchar,
"serveis_publics" varchar,
"serveis_tecnics" varchar,
"serveis_ambientals" varchar,
"serveis_radio" varchar,
"aparcament" varchar,
"estacions_servei" varchar,
"agricola" varchar,
"ramader" varchar,
"forestal" varchar,
"lleure" varchar,
"ecologic" varchar,
"fondaria_edif" varchar,
"edificabilitat" varchar,
"ocupacio" varchar,
"densitat_hab" varchar,
"vol_max_edif" varchar,
"fondaria_edif_pb" varchar,
"pb" varchar,
"alcada" varchar,
"punt_aplic" varchar,
"sep_min" varchar,
"constr_aux_alcada" varchar,
"constr_auxo_cupacio" varchar,
"tanques" varchar,
"nplantes" varchar,
"alcada_lliure" varchar,
"entresol_pb" varchar,
"sotacoberta" varchar,
"pendent" varchar,
"terrasses" varchar,
"elem_sort" varchar,
"cossos_sort" varchar,
"cossos_annexes" varchar,
"porxos" varchar,
"tract_facana" varchar,
"comp_facana" varchar,
"prop_obertura" varchar,
"material_facana" varchar,
"material_coberta" varchar,
"fusteria" varchar,
"espai_lliure" varchar,
"altell" varchar,
"altres" varchar,
"front_min" varchar,
"parce_min" varchar,
"prof_min" varchar,
PRIMARY KEY ("id") 
);
ALTER TABLE "data"."rpt_planejament" OWNER TO "gisadmin";

END;
 
$BODY$
  LANGUAGE 'plpgsql' VOLATILE COST 100
;

ALTER FUNCTION "data"."create_report"() OWNER TO "gisadmin";