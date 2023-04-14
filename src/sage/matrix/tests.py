"""
TESTS:

We test various degenerate cases of kernel computation::

    sage: matrix(ZZ,1,0).kernel()
    Free module of degree 1 and rank 1 over Integer Ring
    Echelon basis matrix:
    [1]
    sage: matrix(QQ,1,0).kernel()
    Vector space of degree 1 and dimension 1 over Rational Field
    Basis matrix:
    [1]
    sage: matrix(GF(7), 1, 0).kernel()                                                  # optional - sage.rings.finite_rings
    Vector space of degree 1 and dimension 1 over Finite Field of size 7
    Basis matrix:
    [1]
    sage: matrix(Frac(QQ['x']),1,0).kernel()
    Vector space of degree 1 and dimension 1 over Fraction Field of Univariate Polynomial Ring in x over Rational Field
    Basis matrix:
    [1]

    sage: matrix(ZZ,0,1).kernel()
    Free module of degree 0 and rank 0 over Integer Ring
    Echelon basis matrix:
    []
    sage: matrix(QQ,0,1).kernel()
    Vector space of degree 0 and dimension 0 over Rational Field
    Basis matrix:
    []
    sage: matrix(GF(7), 0, 1).kernel()                                                  # optional - sage.rings.finite_rings
    Vector space of degree 0 and dimension 0 over Finite Field of size 7
    Basis matrix:
    []
    sage: matrix(Frac(QQ['x']),0,1).kernel()
    Vector space of degree 0 and dimension 0 over Fraction Field of Univariate Polynomial Ring in x over Rational Field
    Basis matrix:
    []

Division by a scalar::

    sage: matrix(QQ, 2, 2, [1, 1, 1, 1]) / 2
    [1/2 1/2]
    [1/2 1/2]
    sage: matrix(QQ, 2, 2, [1, 1, 1, 1]) / (1/2)
    [2 2]
    [2 2]
    sage: matrix(QQ['x,y'], 2, 2, [1, 1, 1, 1]) / x                                     # optional - sage.symbolic
    [1/x 1/x]
    [1/x 1/x]
    sage: A = matrix(CC, 2, 2, [1, 1, 1, 1]) / I; A
    [-1.00000000000000*I -1.00000000000000*I]
    [-1.00000000000000*I -1.00000000000000*I]
    sage: A.parent()
    Full MatrixSpace of 2 by 2 dense matrices over Complex Field with 53 bits of precision

We test an example determinant computation where LinBox gave an incorrect
result::

    sage: L = [-32672924, 402859388, -140623668, 430658721, 106946787, 621276047,-192782447, 431682021, 102255307, 94626176, -34905583, -95358049, 19932420, 123725915, 52076617, -202693998, -104950285, 75183320, 90638691, -10508577, -159993345, 544819075, -205041193, 530536794, 34425198, 812190067, -260981874, 580644585, 123763815, 100094135, -69769038, -119580389, 66415448, 141833716, 62768834, -269408072, -133259211, 100392022, 122810015, -14169559, -116742143, 255636730, -101946387, 229909806, -23983454, 370713224, -122485286, 271167855, 52843557, 36798922, -40542776, -53268126, 45195782, 57579762, 26577120, -124502451, -59510085, 46572885, 57450083, -6605856, 15000427, -30582942, 12516546, -26821359, 4119829, -44014478, 14639368, -32285711, -6171530, -4068360, 4862805, 6668897, -5647699, -6841120, -3067309, 14771590, 7115903, -5537058, -6739292, 775422, 7350404, 230921981, -76923414, 258735233, 86438125, 362368415, -110372559, 248213386, 62007340, 60606320, -15120637, -56148382, 2793135, 76364724, 31673380, -117264550, -61940375, 43368039, 52065723, -6050134, -151307549, 78679036, -46266959, 18647207, -117585287, 85433954, -37642136, 80027656, 2018840, -16574471, -34635562, -6981346, 53375886, -7793292, 519003, -33205642, -9545608, 12868856, 17687995, -1966305, -363614357, 1120703653, -426407076, 1075510629, 37584638, 1662076505, -536823334, 1193214389, 250295666, 197458670, -149948886, -243590352, 148290926, 284338202, 126789390, -552585008, -271574842, 206055077, 252487220, -29112407, -24118132, 125489794, -45531102, 127679943, 19878772, 189727909, -59873328, 133891226, 30235317, 26062022, -13427908, -28437884, 11088522, 35371542, 15314003, -62344332, -31541764, 23159538, 28169710, -3257928, 23875931, -55361113, 21777071, -50092756, 4072588, -80196200, 26290253, -58432798, -11789547, -8211985, 8277760, 11589279, -9463444, -12750488, -5909614, 26780705, 12871707, -9986858, -12330558, 1418788, -123640072, 350287850, -134402037, 331686546, 2311861, 516848375, -167690026, 372647615, 77107961, 59330726, -48837778, -74960963, 49935779, 86475403, 39012673, -172208210, -84008378, 64235307, 78969119, -9098718, 29206401, -58665698, 23367942, -51628286, 7704232, -84008009, 27841118, -62026237, -12049237, -7882950, 9778971, 11364995, -11528692, -12326307, -6027486, 28258762, 13229006, -10541794, -13232024, 1518814, -15226123, -162474710, 52643231, -186629243, -70538436, -257338018, 77581589, -174915120, -44964751, -45100633, 8768165, 39990351, 1319955, -55787679, -23007336, 82911599, 44234087, -30609520, -36691281, 4268583, -3067101, -187862053, 62406108, -208934856, -67593203, -293436726, 89390112, -201449078, -50438313, -48568925, 12749582, 44690794, -3756544, -61132699, -25770007, 94967436, 49821864, -35071658, -42392728, 4922722, -83860746, 387091065, -141493308, 390611827, 53261700, 584183024, -185296915, 413534644, 91854856, 78421794, -44059309, -86512345, 37363320, 106897933, 46669076, -192648548, -96693655, 71636948, 87410231, -10100657, -56763493, 123532651, -49071162, 111379401, -11435705, 179568616, -59393552, 131295311, 25428711, 17842335, -20018876, -25373934, 22014146, 27645710, 12901369, -60462971, -28718167, 22624087, 28023128, -3220309, 74635684, 42414796, -4598855, 80612787, 85891705, 84744646, -20275295, 47713903, 20441907, 28852448, 11300266, -16245887, -24534126, 30219206, 10703344, -24779029, -16921909, 8890606, 9568309, -1154549, -129928022, 450121954, -169305350, 439469539, 30630839, 672148465, -215901643, 479926644, 102311525, 83254236, -57276284, -99501795, 53823660, 117995313, 51970498, -222955007, -110479289, 83108429, 101494954, -11712185, -144442660, 396456359, -153843052, 373857888, -1782212, 585684397, -190815470, 422383108, 85815948, 66107666, -56349192, -86531733, 56862804, 97958280, 43498721, -195572942, -95613139, 73115455, 89344289, -10295212, 10964325, -5070815, 2648146, -839025, 8356359, -4976355, 2255047, -5129380, -209043, 1262716, 2672540, -558453, -4261247, 1210201, -101067, 2031870, 246414, -752782, -1334683, 146103, 117556641, -635133625, 229805379, -649558626, -106084208, -963569121, 304047081, -678780364, -153015989, -133365649, 68083651, 144472798, -54146381, -180316114, -77858131, 316948599, 160367139, -117807494, -143206514, 16562032]
    sage: M = Matrix(Integers(),20,20,L)
    sage: M.det()
    3951360

Test that a certain bug in GP's mathnf was fixed::

    sage: a = gp('Mat([-15,18,-23,-20,-32,11,-19,2,-1,15,22,29,-29,3,-31,25,11,-6,32,7; -31,0,30,-27,-15,13,-21,6,-27,6,3,-4,-4,-28,-30,-16,29,-4,29,-20; -15,-19,-30,9,-18,-31,23,-15,15,-9,20,10,-29,9,18,-6,-1,-20,19,-29; 2,-32,4,-13,17,21,12,-32,12,0,27,-10,-31,-33,-8,-31,-23,25,-18,6; -10,33,4,27,1,25,1,6,31,-7,3,30,23,-4,18,16,-12,21,0,4; -19,20,31,-34,-24,20,-13,-2,18,12,-18,33,22,0,0,10,-25,-29,6,-23; -15,-33,27,-9,-21,-20,5,-20,-31,-11,20,19,31,25,16,20,5,23,-32,-2; 20,18,12,-10,-3,-29,-14,4,-9,21,7,-34,6,16,7,10,11,-21,8,28; 10,-4,-11,-8,-29,33,-23,21,-3,-17,21,7,-28,-10,-16,-1,-29,32,12,16; 13,33,-7,15,-31,20,22,33,21,8,-24,20,27,30,24,20,-29,31,-20,-16; -24,-16,24,-8,7,-22,3,12,-1,-4,-9,10,13,-2,-14,-4,-3,-26,28,-25; 7,-7,19,-26,25,-27,33,12,6,3,31,-30,-14,6,-17,11,-6,5,15,0; 9,-32,-14,9,12,-8,-19,22,20,-23,14,29,-17,-28,-34,-10,4,26,-3,-14; 7,-13,-16,32,-2,11,-2,3,33,-22,-7,-3,12,-24,-7,-7,-1,31,26,22; 8,7,30,29,26,-12,13,21,-18,-5,-27,-33,1,16,-34,-10,-1,8,6,20; 32,-30,27,-21,33,5,14,30,13,24,10,-23,30,-18,13,25,0,-22,18,-19; -4,-6,7,28,-4,9,32,21,29,2,-7,7,-24,-10,2,-9,-23,-18,6,5; 3,19,0,23,-24,-16,-33,-15,-2,16,2,19,28,33,-16,32,-20,-15,28,-18])')
    sage: a.mathnf(1)[1][1,] == gp('[4, 2, 1, 0, 3, 1, 1, 0, 1, 1, 2, 2, 3, 3, 0, 0, 1, 3]')
    True

"""
