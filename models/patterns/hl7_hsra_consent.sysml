package HL7HSRAConsent {
    doc
    /*
     * Curated HL7-HSRA specification pattern: Consent & Authorization.
     *
     * Intent: capture, as a reusable requirement, the constraint that access
     *   to a patient's health information is permitted only when a valid
     *   consent covering the requested purpose exists.
     * Parameters: the data subject, the requested purpose and the consent.
     * Applicability: any HSRA service that discloses or processes personal
     *   health information.
     */

    attribute def Text;
    attribute def Flag;

    part def DataSubject {
        doc /* The patient whose information is governed by consent. */
        attribute subjectId : Text;
    }

    part def Consent {
        doc /* A recorded permission granted by a data subject. */
        attribute purpose : Text;
        attribute valid : Flag;
    }

    requirement def ConsentRequiredPattern {
        doc
        /*
         * Reusable requirement: information may be processed only for a purpose
         * covered by a valid consent of the data subject. The applicable
         * consent's 'valid' flag must be true for the requested purpose.
         */
        subject theSubject : DataSubject;

        attribute requestedPurpose : Text;
        part consent : Consent;
    }
}
