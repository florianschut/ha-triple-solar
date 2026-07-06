"""GraphQL mutation for updating PvtHeatPumpSettings."""

from gql import gql

UPDATE_HEAT_PUMP_SETTINGS_MUTATION = gql("""
mutation SetHeatPumpSettings(
  $id: String!
  $settings: HeatPumpSettingsInput!
  $advanced: Boolean!
  $isExpert: Boolean!
) {
  heatPumpSettings(id: $id, settings: $settings) {
    id
    ...HeatPumpSettingsFragment_1NcsHF
  }
}

fragment HeatPumpSettingsFragment_1NcsHF on HeatPump {
  settings {
    spaceConditioning {
      isHeatingEnabled
      isCoolingEnabled
      spaceCoolingSinkSupplySetpTemp
      spaceHeatingOTMaxSinkSupplySetpTemp
      heatingCurve {
        startAmbientTemp
        ambientTempNeg20SinkSupplySetpTemp
        ambientTempNeg10SinkSupplySetpTemp
        ambientTemp0SinkSupplySetpTemp
        ambientTemp10SinkSupplySetpTemp
        ambientTemp20SinkSupplySetpTemp
        ... on MantovaHeatingCurveSettings {
          startDegreeMinutes
        }
      }
      coolingCurve {
        startAmbientTemp
        ambientTemp20SinkSupplySetpTemp
        ambientTemp30SinkSupplySetpTemp
        ambientTemp40SinkSupplySetpTemp
        ... on MantovaCoolingCurveSettings {
          startDegreeMinutes
        }
      }
      ... on MantovaSpaceConditioningSettings {
        spaceConditioningControlType
        spaceHeatingRoomSetpTemp
        spaceHeatingRoomSetpLowerHysteresis
        spaceCoolingRoomSetpTemp
        spaceCoolingRoomSetpUpperHysteresis
      }
      ... on PikaSpaceConditioningSettings {
        spaceHeatingControlType
        spaceCoolingControlType
        spaceHeatingSinkSupplySetpTemp
        spaceHeatingSchedulerEnabled
        spaceHeatingSchedulerEntries {
          profile
          days
          from
          to
        }
        spaceHeatingProfile
        spaceHeatingProfileNormal {
          heatingCurveOffset
          maxModulationPerc
        }
        spaceHeatingProfileEco {
          heatingCurveOffset
          maxModulationPerc
        }
        spaceHeatingProfileComfort {
          heatingCurveOffset
          maxModulationPerc
        }
      }
    }
    dhw {
      isDHWEnabled
      autoSetpTemp
      dhwSetpLowerHysteresis
      isLegionellaEnabled
      legionellaDay
      schedulerEnabled
      ... on MantovaDHWSettings {
        schedulerTime
        schedulerBlockingStartTime
        schedulerBlockingEndTime
        isSchedulerBlockingEnabled
        isSchedulerForcingEnabled
      }
      ... on PikaDHWSettings {
        modulationPerc
        schedulerEntries {
          profile
          days
          from
          to
          force
        }
        profile
        profileEco {
          tankTempHystLow
          tankTempSetpoint
          modulationPerc
        }
        profileComfort {
          tankTempHystLow
          tankTempSetpoint
          modulationPerc
        }
        profileNormal {
          tankTempHystLow
          tankTempSetpoint
          modulationPerc
        }
      }
    }
    sinkPump @include(if: $advanced) {
      heatingDT
      coolingDT
      startUpPerc
      minPerc
      maxPerc
    }
    sourcePump @include(if: $advanced) {
      heatingDT
      coolingDT
      startUpPerc
      minPerc
      maxPerc
    }
    ... on PikaSettings {
      compressor @include(if: $advanced) {
        maxModulationPerc
        minModulationPerc
        compressorMinOffMin @include(if: $isExpert)
      }
      general {
        spaceConditioningToDHWPrioWeight @include(if: $advanced)
        isBeta
      }
      spaceHeatingUnlockSettings {
        otExternalUnlockPolicyType
        otExternalWaitTimeMinutes
        otExternalBivalentConfigEnabled
        otExternalBivalentConfigAmbientTemp
        otExternalBivalentConfigSourceReturnTemp
        resistanceHeaterUnlockPolicyType
        resistanceHeaterWaitTimeMinutes
        resistanceHeaterBivalentConfigEnabled
        resistanceHeaterBivalentConfigAmbientTemp
        resistanceHeaterBivalentConfigSourceReturnTemp
      }
      dhwUnlockSettings {
        resistanceHeaterUnlockPolicyType
      }
    }
    hardware {
      ... on PikaHardwareSettings {
        aemResistanceHeater {
          canDHW
          canSH
          phase1Allowed
          phase2Allowed
          phase3Allowed
          sinkSupplyTempOffset
        }
        onOffExternalHeater {
          hasOnOffRelayAndSensor
          canDHW
          canSH
          modulationPercThreshold
          sinkSupplyTempHystUp
          sinkSupplyTempHystLow
          sinkSupplyTempOffset
        }
        otExternal {
          canSH
          sinkSupplyTempOffset
        }
      }
      ... on MantovaHardwareSettings {
        otExternal {
          canSH
        }
      }
    }
  }
  id
}
""")
