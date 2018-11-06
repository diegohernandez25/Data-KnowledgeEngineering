declare namespace functx = "http://www.functx.com";
declare function functx:day-of-week
  ( $date as xs:anyAtomicType? )  as xs:integer? {

  if (empty($date))
  then ()
  else xs:integer((xs:date($date) - xs:date('1901-01-06'))
          div xs:dayTimeDuration('P1D')) mod 7
 } ;
declare function functx:day-of-week-pt( $date as xs:anyAtomicType? )  as xs:string? {
  let $dow:=functx:day-of-week($date)
  return(
    switch($dow)
      case 1 return "segunda-feira"
      case 2 return "terça-feira"
      case 3 return "quarta-feira"
      case 4 return "quinta-feira"
      case 5 return "sexta-feira"
      case 6 return "sabado"
      default return "domingo"
    )
};


declare function local:get_salas() as item(){
  <salas>{
    for $sala in distinct-values(doc('horarios_database')//sala)
    return <sala>{$sala}</sala>
  }</salas>
};

declare function local:is_sala_sem_aula($sala as xs:string,$inicio as xs:time,$fim as xs:time,$diadasemana as xs:string) as xs:boolean{
  
    let $cnt:=count(
      for $aula in doc('horarios_database')//aula
      where $aula/@dia_da_semana=$diadasemana and 
            $aula/sala=$sala and
            ($inicio<=$aula/inicio and $fim>$aula/inicio or
            $inicio>$aula/inicio and $inicio<$aula/fim)
      return <unmatch/>)
      
    return $cnt=0
};

declare function local:sala_reservada($sala as xs:string,$inicio as xs:time,$fim as xs:time,$dia as xs:date) as item(){
  let $cnt:=count(
      for $ent in doc('reservas_database')//entrada[@dia=xs:string($dia) and @sala=$sala]
      where $inicio<=$ent/@inicio and $fim>$ent/@inicio or
            $inicio>$ent/@inicio and $inicio<$ent/@fim
      return <unmatch/>)
  return $cnt!=0
};

declare updating function local:reservar_sala($nmec as xs:integer,$sala as xs:string,$inicio as xs:time,$fim as xs:time,$dia as xs:date){
  
  if(local:is_sala_sem_aula($sala,$inicio,$fim,functx:day-of-week-pt($dia)) and local:sala_reservada($sala,$inicio,$fim,$dia)=(0=1))
  then(
    (:free spot:)
    insert node <entrada nmec="{$nmec}" sala="{$sala}" dia="{$dia}" inicio="{$inicio}" fim="{$fim}"/> into doc('reservas_database')/reserva
  )
};

declare function local:get_salas_livres($inicio as xs:time,$fim as xs:time,$dia as xs:date) as item(){
  <salas>{
    for $sala in local:get_salas()/sala/text()
    where local:is_sala_sem_aula($sala,$inicio,$fim,functx:day-of-week-pt($dia)) and local:sala_reservada($sala,$inicio,$fim,$dia)=(0=1)
    return <sala>{$sala}</sala>
  }</salas>
};

declare function local:get_reservas($nmec as xs:integer,$dia as xs:date) as item(){
  <reservas>{
    for $reserva in doc('reservas_database')//entrada[@nmec=$nmec and @dia=$dia]
    return $reserva
  }</reservas>
};

(: local:get_salas_sem_aula(xs:time("17:00:00"),xs:time("20:00:00"),xs:date("2018-11-05")) :)
(: local:reservar_sala(80313,"04.1.02",xs:time("01:00:00"),xs:time("02:00:00"),xs:date("2018-11-05")) :)
(:local:reservar_sala("80313","04.1.02",xs:time("11:00:00"),xs:time("12:00:00"),xs:date("2018-11-05")):)
(: local:sala_reservada("04.1.02",xs:time("12:00:00"),xs:time("13:00:00"),xs:date("2018-11-05")) :)
(: functx:day-of-week-pt(xs:date("2018-11-05")) :)
(: local:sala_reservada("04.1.06",xs:time("13:00:00"),xs:time("14:00:00"),xs:date("2018-11-04")) :)
(: local:get_salas_livres(xs:time("09:00:00"),xs:time("10:00:00"),"segunda-feira") :)
(: local:is_sala_livre("04.1.06",xs:time("13:00:00"),xs:time("14:00:00"),"segunda-feira") :)
(: local:get_salas():) 