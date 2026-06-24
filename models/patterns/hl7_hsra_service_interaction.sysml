package HL7HSRAServiceInteraction {
    doc
    /*
     * Curated HL7-HSRA specification pattern: Service Interaction.
     *
     * Intent: model a request/response interaction between two healthcare
     *   service participants (a requester and a provider) that exchange an
     *   information payload, as a reusable parametric definition.
     * Parameters: the participant roles and the exchanged payload.
     * Applicability: any HSRA service that follows a request/response exchange.
     */

    // Local primitive types (the Kernel scalar library is resolved by the
    // deployed repository at load time; defined locally here so the model is
    // self-contained and type-complete for offline syntactic validation).
    attribute def Text;

    part def Participant {
        doc /* A party that takes part in a service interaction. */
        attribute name : Text;
        attribute role : Text;
    }

    part def InformationPayload {
        doc /* The information exchanged during an interaction. */
        attribute identifier : Text;
        attribute contentType : Text;
    }

    part def ServiceInteractionPattern {
        doc
        /*
         * Reusable request/response interaction. Usages instantiate this
         * definition by binding the requester, provider and payload.
         */
        attribute interactionName : Text;

        part requester : Participant;
        part provider : Participant;
        part payload : InformationPayload;
    }
}
