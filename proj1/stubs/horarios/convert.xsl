<?xml version="1.0"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:xsk="http://www.w3.org/1999/XSL/Transform">


        <xsl:variable name="root" select="/"/>
        <xsl:template match="/">
            <cursos>
                <xsl:for-each select="distinct-values((//tr/*[12])[position()>1]/font/text())">
                    <curso>
                        <xsl:variable name="cod_curso" select="."/>
                        <xsl:attribute name="codigo">
                            <xsl:value-of select="$cod_curso"/>
                        </xsl:attribute>

                        <xsl:element name="nome">
                            <xsl:value-of select="$root//tr[*[12]/font/text()=$cod_curso][1]/*[13]"/>
                        </xsl:element>
                        <cadeiras>
                            <xsl:for-each select="distinct-values(($root//tr[position()>1][*[12]=$cod_curso]/*[5])/font/text())">
                                <cadeira>

                                    <xsl:variable name="cod_cadeira" select="."/>
                                    <xsl:attribute name="codigo">
                                        <xsl:value-of select="$cod_cadeira"/>
                                    </xsl:attribute>

                                    <xsl:variable name="cadeira" select="$root//tr[*[5]/font/text()=$cod_cadeira and *[12]/font/text()=$cod_curso][1]"/>

                                    <xsl:element name="nome">
                                        <xsl:value-of select="$cadeira/*[6]"/>
                                    </xsl:element>

                                    <xsl:element name="ano">
                                        <xsl:value-of select="$cadeira/*[14]"/>
                                    </xsl:element>

                                    <turmas>
                                        <xsl:for-each select="distinct-values($root//tr[position()>1][*[5]/font/text()=$cod_cadeira and *[12]/font/text()=$cod_curso]/*[7]/font/text())">
                                           <turma>

                                               <xsl:variable name="turno_turma" select="."/>
                                                <xsl:attribute name="turno">
                                                    <xsl:value-of select="$turno_turma"/>
                                                </xsl:attribute>

                                               <xsl:variable name="tipo_turma" select="($root//tr[*[5]=$cod_cadeira and *[7]=$turno_turma]/*[10])[1]"/>

                                               <xsl:attribute name="tipo">
                                                   <xsl:value-of select="$tipo_turma"/>
                                               </xsl:attribute>

                                                           <horarios>
                                                                   <xsl:for-each select="distinct-values(($root//tr[position()>1][*[5]=$cod_cadeira and *[7]=$turno_turma]/*[8])/font/text())">
                                                                       <aula>

																		   <xsl:variable name="dia" select="."/>
                                                                           <xsl:variable name="turma_aula" select="($root//tr[*[5]=$cod_cadeira and *[7]=$turno_turma and *[8]=$dia])[1]"/>

                                                                           <xsl:attribute name="dia_da_semana">
                                                                               <xsl:if test="$dia='0'">
                                                                                   <xsl:text>segunda-feira</xsl:text>
                                                                               </xsl:if>
                                                                               <xsl:if test="$dia='1'">
                                                                                   <xsl:text>terça-feira</xsl:text>
                                                                               </xsl:if>
                                                                               <xsl:if test="$dia='2'">
                                                                                   <xsl:text>quarta-feira</xsl:text>
                                                                               </xsl:if>
                                                                               <xsl:if test="$dia='3'">
                                                                                   <xsl:text>quinta-feira</xsl:text>
                                                                               </xsl:if>
                                                                               <xsl:if test="$dia='4'">
                                                                                   <xsl:text>sexta-feira</xsl:text>
                                                                               </xsl:if>
                                                                               <xsl:if test="$dia='5'">
                                                                                   <xsl:text>sabado</xsl:text>
                                                                               </xsl:if>
                                                                           </xsl:attribute>

                                                                           <xsl:element name="sala">
                                                                               <xsl:value-of select="$turma_aula/*[4]"/>
                                                                           </xsl:element>
                                                                           <xsl:element name="inicio">
                                                                               <xsl:value-of select="$turma_aula/*[2]"/>
                                                                           </xsl:element>
                                                                           <xsl:element name="fim">
                                                                               <xsl:value-of select="$turma_aula/*[3]"/>
                                                                           </xsl:element>

                                                                       </aula>
                                                                   </xsl:for-each>



                                                           </horarios>

                                                       </turma>
                                                    </xsl:for-each>
                                                </turmas>

                                </cadeira>
                            </xsl:for-each>
                        </cadeiras>
                    </curso>
                </xsl:for-each>
            </cursos>

        </xsl:template>




</xsl:stylesheet>
