(:
declare function local:get_ucs_ano($cod as xs:integer, $ano as xs:integer) as item(){
  <cadeiras>{
    for $cadeira in doc('horarios_database')//cadeira[../../@codigo=$cod]
    where $cadeira/ano=$ano
    return $cadeira
  }</cadeiras>
};

let $aaa:=local:get_ucs_ano(8240,4)
return $aaa
:)

declare function local:get_uc($cod as xs:integer) as item(){
    for $cadeira in doc('horarios_database')//cadeira
    where $cadeira/@codigo=xs:string($cod)
    return $cadeira 
};


(:
declare function local:get_turmas_by_type($cod as xs:integer, $type as xs:string) as item(){
  <turmas>{
    for $turma in doc('horarios_database')//turma[../../@codigo=$cod]
    where $turma/@tipo=$type
    return $turma
  }</turmas>
};


let $aaa:=local:get_turmas_by_type(47092, "T")
return $aaa
:)

declare function local:get_turma($cod as xs:integer, $turma_val as xs:string) as item(){
  <turma>{
  for $turma in doc('horarios_database')//turma[../../@codigo=$cod]
    where $turma/@turno=$turma_val
    return $turma
  }</turma>
};

declare function local:get_turma_hours($cod as xs:integer, $turno as xs:string) as item(){
  <aulas>{
    for $turma in doc('horarios_database')//turma[../../@codigo=$cod]
    where $turma/@turno=$turno
    return $turma//aula
  }</aulas>

};



(: given class and list of taken times, check if class can be chosen without overlap:)

declare function local:fits_horario($used as item(), $new as item()) as item() {
  let $cnt:=count(
  for $aula in $used//aula
  where $aula/@dia_da_semana=$new//aula/@dia_da_semana and
  ($new//aula/inicio<=$aula/inicio and $new//aula/fim>$aula/inicio or
          $new//aula/inicio>$aula/inicio and $new//aula/inicio<$aula/fim)
  return <unmatch/>)
    return $cnt=0
};


(:
declare function local:test() as item(){
  let $a := local:get_turma_hours(47112, "T")
  
  return local:fits_horario(local:get_turma_hours(47022, "P1"), local:get_turma_hours(42566, "P1"))
};
:)
  
declare updating function local:append_turma($turmas as item(), $turma as item()) {
  insert node $turma into $turmas
};


let $aaa := local:append_turma(local:get_turma(47022, "P1"), local:get_turma(42566, "P2"))
return $aaa