declare function local:get_ucs_ano($cod as xs:integer, $ano as xs:integer) as item(){
  <cadeiras>{
    for $cadeira in doc('horarios_database')//cadeira[../../@codigo=$cod]
    where $cadeira/ano=$ano
    return $cadeira
  }</cadeiras>
};

declare function local:get_uc($cod as xs:integer, $curso as xs:integer) as item(){
    for $cadeira in doc('horarios_database')//cadeira[../../@codigo=$curso]
    where $cadeira/@codigo=xs:string($cod)
    return $cadeira 
};


declare function local:get_turmas_by_type($cod as xs:integer, $type as xs:string) as item(){
  <turmas>{
    for $turma in doc('horarios_database')//turma[../../@codigo=$cod]
    where $turma/@tipo=$type
    return $turma
  }</turmas>
};


declare function local:get_turma($cod as xs:integer, $curso as xs:integer, $turma_val as xs:string) as item(){
  for $turma in doc('horarios_database')//turma[../../@codigo=$cod and ../../../../@codigo=$curso]
    where $turma/@turno=$turma_val
    return $turma
};

declare function local:get_turma_hours($cod as xs:integer, $turno as xs:string) as item(){
  <aulas>{
    for $turma in doc('horarios_database')//turma[../../@codigo=$cod]
    where $turma/@turno=$turno
    return $turma//aula
  }</aulas>

};

declare function local:fits_horario($id as xs:integer, $uc as xs:integer, $turma as xs:string) as item() {
  let $new := local:get_turma_hours($uc, $turma)
  let $cnt:=count(
  for $aula in doc('self_horarios')//aula[../../../../../@id=$id]
  where $aula/@dia_da_semana=$new//aula/@dia_da_semana and
  ($new//aula/inicio<=$aula/inicio and $new//aula/fim>$aula/inicio or
          $new//aula/inicio>$aula/inicio and $new//aula/inicio<$aula/fim)
  return <unmatch/>)
    return $cnt=0
};

declare updating function local:create_tmp_horario($file as xs:string) {
  db:create("self_horarios", <options/>, $file)
};

declare updating function local:delete_tmp_horario() {
  db:drop("self_horarios")
};
  
declare updating function local:create_option($id as xs:integer) {
  insert node <cadeiras id="{$id}"/> into doc("self_horarios")/options
};

declare updating function local:append_cadeira_step1($id as xs:integer, $curso as xs:integer, $uc as xs:integer) {
  insert node local:get_uc($uc, $curso) into doc("self_horarios")//cadeiras[@id=$id]
};

declare updating function local:append_cadeira_step2($id as xs:integer, $uc as xs:integer) {
  for $turma in doc("self_horarios")//turma[../../@codigo=$uc and ../../../@id=$id]
  return delete nodes $turma
};

declare updating function local:append_turma($id as xs:integer, $curso as xs:integer, $uc as xs:integer, $turma as xs:string) {
    insert nodes local:get_turma($uc, $curso, $turma) into doc("self_horarios")//turmas[../@codigo=$uc and ../../@id=$id]
};

declare updating function local:del_option($id) {
  for $cadeiras in doc("self_horarios")//cadeiras
  where $cadeiras/@id=$id
  return delete node $cadeiras
};

declare function local:count_options() {
  count(doc("self_horarios")//cadeiras)
};

declare function local:get_current_horario() {
  let $doc := doc("self_horarios")
  return $doc
};


(: local:get_ucs_ano(8240, 3) :)
(: local:delete_tmp_horario() :)
(: local:create_tmp_horario("/home/amargs/Dropbox/deti/edc/proj/edc-2018/stubs/horarios/tmp.xml") :)
(: local:create_option(1) :)
(: local:append_cadeira_step1(1,8240,42509) :)
(: local:append_cadeira_step2(1, 42509) :)
(: local:append_turma(1, 8240, 42509, "P1") :)
(: local:fits_horario(1, 42566, "P1") :)
(: doc("self_horarios") :)
(: local:del_option(1) :)

(: local:get_uc(47139, 8240) :)