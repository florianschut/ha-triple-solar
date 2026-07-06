"""GraphQL query for fetching heat pump status."""

from gql import gql

HEAT_PUMP_STATUS_QUERY = gql("""
query HeatPumpStatus($id: String!, $refresh: Boolean, $isAdmin: Boolean!) {
  heatPump(id: $id, refresh: $refresh) {
    id
    name
    alerts {
      code
      severity
      message
    }
    softwareVersion @include(if: $isAdmin)
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
          __typename
        }
        coolingModulationLevels {
          heatPump
          __typename
        }
        __typename
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
          __typename
        }
        __typename
      }
      __typename
    }
    heatPumpModule {
      sensors {
        sourceReturnTemp
        sourceSupplyTemp
        sinkReturnTemp
        sinkSupplyTemp
        sinkPumpFlow
        sourcePumpFlow
        __typename
      }
      __typename
    }
    externalDevice {
      sinkSupplyTemp
      sinkSupplySetpTemp
      sinkReturnTemp
      modulationPerc
      hasHeatingDemand
      hasFault
      oemFaultCode
      __typename
    }
    resistanceHeater {
      sinkSupplyTemp
      sinkSupplySetpTemp
      modulationPerc
      hasHeatingDemand
      __typename
    }
    settings {
      dhw {
        dhwSetpLowerHysteresis
        __typename
      }
      ... on PikaSettings {
        general {
          isBeta
        }
      }
      __typename
    }
    ... on PikaHeatPump {
      pressures {
        sink
        source
      }
      id
    }
    __typename
  }
}
""")
