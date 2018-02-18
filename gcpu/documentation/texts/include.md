
Inkludering
===========

Gcpu-kompilatorn till�ter att kod skrivs i en eller flera separata filer som sedan sammanl�nkas till ett program under kompilationen. Detta f�r att g�ra det enkelt att strukturera koden samt att enkelt dela samma kod mellan flera olika program.
F�r att inkludera kod fr�n en annan file anv�nds nyckelordet `#import <filnamn>`

Om exmpelvis f�ljande kod finns i en fil kallad *matte.g*

    %kvadratrot
    herp
    endf

kan kvadratrotsfunctionen inkluderas i programmet med nyckelorder `#import matte`. Definitioner och funktioner som inlkuderas i en fil blir tillg�ngliga under `<k�llfil>_<namn>`. Exempelvis blir kvadratrotsfunktionen definierad ovan tillg�nglig som `matte_kvadratrot`.
F�r att ber�kna kvadratroten av 9 kan exempelvis f�ljande kod anv�ndas i huvudfilen:

    #import matte

    %main

    arg 9
    call matte_kvadratrot
    print a

    endf

Inkluderade definitioner f�r behandlas precis som lokala definitioner i en fil. Om en inkluderad definition anv�nds ofta och prefixet `<k�llfil>_` anses on�digt kan den d�pas om med `#def`. Exempelvis `#def sqrt = matte_kvadratrot` g�r att funktionen kan anropas b�de som `sqrt` och `matte_kvadratrot`.
Vid inkludering av en fil �r det endast de lokala definitionerna som inkluderas. Nyckelord, redan inkluderad samt globala definitioner f�rs inte vidare s�vida de inte �r omdefinierade med `#def`

Inkluderade funktioner kommer precis som lokala genomg� sortering utifr�n de kan n�s via referenser fr�n rotfunktionen som diskuterat i **TBD**.

Inkluderinsloopar
-----------------

Det �r inte till�tet att skapa s� kallade inkluderingsloopar d�r tv� eller fler filer inkluderar varandra. Exemelvis kommer f�ljande kod inte kompileras
*a.g*

    #import b

*b.g*

    #import a

Detta beror p� att nyckelordet `#import b` tolkas som att filen *b* m�ste kompileras f�re den nuvarande filen. N�r koden ovan kompileras s� tolkas den som att *b* ska kompileras f�re *a* och *a* f�re *b*. Ingen av filerna f�r d�rf�r kompileras f�re den andra och det finns ingen l�mplig plats f�r kompilatorn att starta p�.  
Inkluderingsloopar �r inte begr�nsade till endast tv� filer som i exemplet ovan utan kan inneh�lla ett obegr�nsat antal filer.  
Filer f�r inte heller inkludera sig sj�lva av likv�rdiga sk�l.