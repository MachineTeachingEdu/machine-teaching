/*
 
 Copyright (c) 2012-2017, Michael (Mikhail) Yudelson
 All rights reserved.
 
 Redistribution and use in source and binary forms, with or without
 modification, are permitted provided that the following conditions are met:
 * Redistributions of source code must retain the above copyright
 notice, this list of conditions and the following disclaimer.
 * Redistributions in binary form must reproduce the above copyright
 notice, this list of conditions and the following disclaimer in the
 documentation and/or other materials provided with the distribution.
 * Neither the name of the Michael (Mikhail) Yudelson nor the
 names of other contributors may be used to endorse or promote products
 derived from this software without specific prior written permission.
 
 THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
 ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
 WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 DISCLAIMED. IN NO EVENT SHALL COPYRIGHT HOLDERS AND CONTRIBUTORS BE LIABLE FOR
 ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
 (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
 LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
 ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 
 */

//
// encapsulator of results of a fitting [sub-]job
//

#ifndef __HMM__FitBitSlicedA__
#define __HMM__FitBitSlicedA__

#include "utils.h"

#ifndef __HMM__FitBitEnums__
#define __HMM__FitBitEnums__
enum FIT_BIT_SLOT {
    FBS_PAR       = 1, // e.g. PI
    FBS_PARm1     = 2, // e.g. PIm1
    FBS_PARm2     = 7, // e.g. PIm2
    FBS_GRAD      = 3, // e.g. gradPI
    FBS_GRADm1    = 4, // e.g. gradPIm1
    FBS_PARcopy   = 5, // e.g. PIcopy
    FBS_DIR       = 8, // e.g. gradPIdir
    FBS_DIRm1     = 6  // e.g. gradPIdirm1
};

enum FIT_BIT_VAR {
    FBV_PI = 1, // PI
    FBV_A  = 2, // A
    FBV_B  = 3  // B
};
#endif /* fit bit enums*/

class FitBitSlicedA {
public:
    NPAR nO, nS, nZ; // copies
    NCAT nG, nK; // copies
    NUMBER* pi; // usually a pointer
    NUMBER ***A; // usually a pointer
    NUMBER **B; // usually a pointer
    NUMBER *PIm1; // previous value
    NUMBER ***Am1; // previous value
    NUMBER **Bm1; // previous value
    NUMBER *PIm2; // 2 previous value
    NUMBER ***Am2; // 2 previous value
    NUMBER **Bm2; // 2 previous value
    NUMBER *gradPI; // gradient
    NUMBER ***gradA; // gradient
    NUMBER **gradB; // gradient
    NUMBER *gradPIm1; // previous gradient
    NUMBER ***gradAm1; // previous gradient
    NUMBER **gradBm1; // previous gradient
    NUMBER *PIcopy; // previous value
    NUMBER ***Acopy; // previous value
    NUMBER **Bcopy; // previous value
    NUMBER *dirPI; // step direction
    NUMBER ***dirA; // step direction
    NUMBER **dirB; // step direction
    NUMBER *dirPIm1; // previous step direction
    NUMBER ***dirAm1; // previous step direction
    NUMBER **dirBm1; // previous step direction
    NCAT xndat; // number of sequences of data
    struct data** x_data; // sequences of data
    NPAR projecttosimplex; // whether projection to simplex should be done
    NPAR Cslice; // current slice during L2 norm penalty fitting
    
    FitBitSlicedA(NPAR a_nS, NPAR a_nO, NCAT a_nK, NCAT a_nG, NPAR a_nZ, NUMBER a_tol, NPAR a_tol_mode);
    FitBitSlicedA(NPAR a_nS, NPAR a_nO, NCAT a_nK, NCAT a_nG, NPAR a_nZ, NUMBER a_tol, NPAR a_tol_mode, NPAR a_projecttosimplex);
    ~FitBitSlicedA();
    void init(enum FIT_BIT_SLOT fbs);
    void negate(enum FIT_BIT_SLOT fbs);
    void link(NUMBER *a_PI, NUMBER ***a_A, NUMBER **a_B, NCAT a_xndat, struct data** a_x_data);
    void toZero(enum FIT_BIT_SLOT fbs);
    void destroy(enum FIT_BIT_SLOT fbs);
    void copy(enum FIT_BIT_SLOT sourse_fbs, enum FIT_BIT_SLOT target_fbs);
    void add(enum FIT_BIT_SLOT sourse_fbs, enum FIT_BIT_SLOT target_fbs);
    bool checkConvergence(FitResult *fr);
    void doLog10ScaleGentle(enum FIT_BIT_SLOT fbs);
    
    // adding penalties
    void addL2Penalty(enum FIT_BIT_VAR fbv, param* param, NUMBER factor);
private:
    NUMBER tol;
    NPAR tol_mode;

    void init(NUMBER* &pi, NUMBER*** &A, NUMBER** &B);
    void negate(NUMBER* &pi, NUMBER*** &A, NUMBER** &B);
    void toZero(NUMBER *pi, NUMBER ***A, NUMBER **B);
    void destroy(NUMBER* &pi, NUMBER*** &A, NUMBER** &B);
    void get(enum FIT_BIT_SLOT fbs, NUMBER* &a_PI, NUMBER*** &a_A, NUMBER** &a_B);
    void add(NUMBER *soursePI, NUMBER ***sourseA, NUMBER **sourseB, NUMBER *targetPI, NUMBER ***targetA, NUMBER **targetB);
    void copy(NUMBER* &soursePI, NUMBER*** &sourseA, NUMBER** &sourseB, NUMBER* &targetPI, NUMBER*** &targetA, NUMBER** &targetB);
};

#endif /* defined(__HMM__FitBitSlicedA__) */
