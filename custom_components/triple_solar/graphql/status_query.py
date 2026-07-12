"""GraphQL query for fetching heat pump status."""

from gql import gql

HEAT_PUMP_STATUS_QUERY = gql("""
query HeatPumpStatus($id: String!, $refresh: Boolean) {
  heatPump(id: $id, refresh: $refresh) {
    id
    name
    alerts {
      code
      severity
      message
    }
    softwareVersion
    connectionType
    lastStatus
    controller {
      ... on PikaControllerState {
        programState
      }
      spaceConditioning {
        heatingStatus
        coolingStatus
        isHeatingActive
        isCoolingActive
        hasHeatingDemand
        hasCoolingDemand
        roomTemp
        roomSetpTemp
        heatingModulationLevels {
          heatPump
          resistanceHeater
          external
        }
        coolingModulationLevels {
          heatPump
        }
      }
      domesticHotWater {
        status
        isActive
        hasDemand
        tankTemp
        tankSetpTemp
        modulationLevels {
          heatPump
          resistanceHeater
        }
      }
    }
    heatPumpModule {
      sensors {
        sourceReturnTemp
        sourceSupplyTemp
        sinkReturnTemp
        sinkSupplyTemp
        sinkPumpFlow
        sourcePumpFlow
      }
    }
    externalDevice {
      sinkSupplyTemp
      sinkSupplySetpTemp
      sinkReturnTemp
      modulationPerc
      hasHeatingDemand
      hasFault
      oemFaultCode
    }
    resistanceHeater {
      sinkSupplyTemp
      sinkSupplySetpTemp
      modulationPerc
      hasHeatingDemand
    }
    settings {
      spaceConditioning {
        isHeatingEnabled
        isCoolingEnabled
      }
      dhw {
        dhwSetpLowerHysteresis
        isDHWEnabled
        autoSetpTemp
        ... on PikaDHWSettings {
          profile
          modulationPerc
        }
      }
    }
    ... on PikaHeatPump {
      pressures {
        sink
        source
      }
      id
    }
  }
}
""")
