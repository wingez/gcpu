
Inkludering
===========

Gcpu-kompilatorn tillåter att kod skrivs i en eller flera separata filer som sedan sammanlänkas till ett program under kompilationen. Detta för att göra det enkelt att strukturera koden samt att enkelt dela samma kod mellan flera olika program.
För att inkludera kod från en annan file används nyckelordet `#import <filnamn>`

Om exmpelvis följande kod finns i en fil kallad *matte.g*

    %kvadratrot
    herp
    endf

kan kvadratrotsfunctionen inkluderas i programmet med nyckelorder `#import matte`. Definitioner och funktioner som inlkuderas i en fil blir tillgängliga under `<källfil>_<namn>`. Exempelvis blir kvadratrotsfunktionen definierad ovan tillgänglig som `matte_kvadratrot`.
För att beräkna kvadratroten av 9 kan exempelvis följande kod användas i huvudfilen:

    #import matte

    %main

    arg 9
    call matte_kvadratrot
    print a

    endf

Inkluderade definitioner får behandlas precis som lokala definitioner i en fil. Om en inkluderad definition används ofta och prefixet `<källfil>_` anses onödigt kan den döpas om med `#def`. Exempelvis `#def sqrt = matte_kvadratrot` gör att funktionen kan anropas både som `sqrt` och `matte_kvadratrot`.
Vid inkludering av en fil är det endast de lokala definitionerna som inkluderas. Nyckelord, redan inkluderad samt globala definitioner förs inte vidare såvida de inte är omdefinierade med `#def`

Inkluderade funktioner kommer precis som lokala genomgå sortering utifrån de kan nås via referenser från rotfunktionen som diskuterat i **TBD**.

Inkluderinsloopar
-----------------

Det är inte tillåtet att skapa så kallade inkluderingsloopar där två eller fler filer inkluderar varandra. Exemelvis kommer följande kod inte kompileras
*a.g*

    #import b

*b.g*

    #import a

Detta beror på att nyckelordet `#import b` tolkas som att filen *b* måste kompileras före den nuvarande filen. När koden ovan kompileras så tolkas den som att *b* ska kompileras före *a* och *a* före *b*. Ingen av filerna får därför kompileras före den andra och det finns ingen lämplig plats för kompilatorn att starta på.  
Inkluderingsloopar är inte begränsade till endast två filer som i exemplet ovan utan kan innehålla ett obegränsat antal filer.  
Filer får inte heller inkludera sig själva av likvärdiga skäl.