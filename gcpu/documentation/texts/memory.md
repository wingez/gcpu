
Minnesallokering
================

För att alokera ett object i minnet används nyckelordet `#instance <namn> <typ>`, där <namn> är namnet som minnesobjektet ska refereras som i koden och <typ> är ett objekt som representerar storleken på minnet som ska allokeras.
Exempelvis `#instance min_byte byte` allokerar ett minne av storleken 1 byte i minnet och låter detta område referas som *min_byte* i koden.

De grundläggande typerna och dess storlek är:
| typ | storlek i byte|
|:----|--------------:|
|byte|1|
|dbyte|2|
|tbyte|3|
|qbyte|4|
|ptr|2|

Det går också att definiera arrays med nycelordet `#instance <namn> <typ>[<array_längd>]` där <array_längd> är längden på arrayen som ska allokeras. 
Exempel `#instance min_array byte[6]` allokerar ett område av storleken 6 bytes och gör det tillgängligt under namnet *min_array*. Utöver detta går det att referera de individuella elementen i arrayen med `<array_namn>[<index>]`. `min_array[3]` ger en pekare till det tredje elementet i arrayen.

    #instance 



Fält
-----

För att skapa ett sammanhängande minnessegment med individuelt addresserbara fält användes nyckelordet

    #instance <namn>
        <fältnamn_1> : <fälttyp_1>
        <fältnamn_2> : <fälttyp_2>
        ...
    end

Detta skapar ett minnesområde av storleken *<fälttyp_1> + <fälttyp_2>* och gör det tillgängligt under namnet <namn>. De olika fälten går att referera med `<namn>.<fältnamn>`
Exempelvis:

    #instance min_rektangel
        bredd : byte
        höjd : byte
    end
    
    &main
        mv 6 min_rektangel.bredd
        print min_rektangel.bredd
    end
    
Strukturer
==========

För att skapa en fördefinierad minnesstruktur, så kallad typ, används nyckelordet `#struct` vars syntax är identiskt med `#instance`. Den enda funktionella skillnaden är att typen inte allokeras i minne. Den generarede typen kan sedan allokeras med `#instance <namn> <typ>`.

    #struct rektangel
        bredd:byte
        höjd:byte
    end
    
    #instance min_rektangel1 rektangel
    #instance min_rektangel2 rektangel
    
Nästning
--------

Strukturer går att nästa i varandra

    #instance spelare
        hälsa : byte
        #struct position
            x : byte
            y : byte
        end
    end

    %main
        mv 100 spelare.hälsa
        mv 10 spelare.position.x
        mv 5 spelare.position.y
    end
    
Eller
    
    #struct entity
        hälsa : byte
        #struct position
            x : byte
            y : byte
        end
    end

    #instance player entity
    #instance fiende entity
    

Fördefinierade värden
---------------------

För att skapa ett minnesobjekt med ett fördefinierat innehåll används syntaxet `#instance <namn>:<typ> = <värde>`
Värdet är inte konstant genom programmets livstid utan kan variera. Men detta värdet är garanterat att finnas på denna plats när programmet startar.




