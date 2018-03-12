
Minnesallokering
================

F�r att alokera ett object i minnet anv�nds nyckelordet `#instance <namn> <typ>`, d�r <namn> �r namnet som minnesobjektet ska refereras som i koden och <typ> �r ett objekt som representerar storleken p� minnet som ska allokeras.
Exempelvis `#instance min_byte byte` allokerar ett minne av storleken 1 byte i minnet och l�ter detta omr�de referas som *min_byte* i koden.

De grundl�ggande typerna och dess storlek �r:
| typ | storlek i byte|
|:----|--------------:|
|byte|1|
|dbyte|2|
|tbyte|3|
|qbyte|4|
|ptr|2|

Det g�r ocks� att definiera arrays med nycelordet `#instance <namn> <typ>[<array_l�ngd>]` d�r <array_l�ngd> �r l�ngden p� arrayen som ska allokeras. 
Exempel `#instance min_array byte[6]` allokerar ett omr�de av storleken 6 bytes och g�r det tillg�ngligt under namnet *min_array*. Ut�ver detta g�r det att referera de individuella elementen i arrayen med `<array_namn>[<index>]`. `min_array[3]` ger en pekare till det tredje elementet i arrayen.

    #instance 



F�lt
-----

F�r att skapa ett sammanh�ngande minnessegment med individuelt addresserbara f�lt anv�ndes nyckelordet

    #instance <namn>
        <f�ltnamn_1> : <f�lttyp_1>
        <f�ltnamn_2> : <f�lttyp_2>
        ...
    end

Detta skapar ett minnesomr�de av storleken *<f�lttyp_1> + <f�lttyp_2>* och g�r det tillg�ngligt under namnet <namn>. De olika f�lten g�r att referera med `<namn>.<f�ltnamn>`
Exempelvis:

    #instance min_rektangel
        bredd : byte
        h�jd : byte
    end
    
    &main
        mv 6 min_rektangel.bredd
        print min_rektangel.bredd
    end
    
Strukturer
==========

F�r att skapa en f�rdefinierad minnesstruktur, s� kallad typ, anv�nds nyckelordet `#struct` vars syntax �r identiskt med `#instance`. Den enda funktionella skillnaden �r att typen inte allokeras i minne. Den generarede typen kan sedan allokeras med `#instance <namn> <typ>`.

    #struct rektangel
        bredd:byte
        h�jd:byte
    end
    
    #instance min_rektangel1 rektangel
    #instance min_rektangel2 rektangel
    
N�stning
--------

Strukturer g�r att n�sta i varandra

    #instance spelare
        h�lsa : byte
        #struct position
            x : byte
            y : byte
        end
    end

    %main
        mv 100 spelare.h�lsa
        mv 10 spelare.position.x
        mv 5 spelare.position.y
    end
    
Eller
    
    #struct entity
        h�lsa : byte
        #struct position
            x : byte
            y : byte
        end
    end

    #instance player entity
    #instance fiende entity
    

F�rdefinierade v�rden
---------------------

F�r att skapa ett minnesobjekt med ett f�rdefinierat inneh�ll anv�nds syntaxet `#instance <namn>:<typ> = <v�rde>`
V�rdet �r inte konstant genom programmets livstid utan kan variera. Men detta v�rdet �r garanterat att finnas p� denna plats n�r programmet startar.




