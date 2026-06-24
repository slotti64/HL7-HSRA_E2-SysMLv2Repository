package HL7HSRACapability {
    doc
    /*
     * Curated HL7-HSRA specification pattern: Business Capability / Service.
     *
     * Intent: model an HSRA business capability realised by a service that
     *   performs an activity producing an outcome, as a reusable definition.
     * Parameters: the capability name and the produced outcome.
     * Applicability: any HSRA capability exposed as a service.
     */

    attribute def Text;

    part def Outcome {
        doc /* A result produced by exercising a capability. */
        attribute description : Text;
    }

    action def DeliverService {
        doc /* The activity that realises the capability. */
        out result : Outcome;
    }

    part def CapabilityPattern {
        doc
        /*
         * Reusable capability: a named business capability realised by a
         * service action that delivers an outcome.
         */
        attribute capabilityName : Text;

        action deliver : DeliverService;
        part producedOutcome : Outcome;
    }
}
