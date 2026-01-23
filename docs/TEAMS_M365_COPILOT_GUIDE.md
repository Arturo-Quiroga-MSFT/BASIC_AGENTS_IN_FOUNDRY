# Using WeatherAgent in Teams & Microsoft 365 Copilot

## Overview

The **WeatherAgent** is now published in Azure AI Foundry and can be integrated with Microsoft Teams and Microsoft 365 Copilot. This guide explains how to access and use the agent across Microsoft's productivity platforms.

## Published Agent Details

- **Agent Name**: WeatherAgent
- **Version**: 2
- **Description**: Weather agent with real OpenWeatherMap API integration
- **Capabilities**: Provides real-time weather information for any city worldwide

## Prerequisites

### For End Users
- Microsoft 365 account with access to Microsoft 365 Copilot
- Access to Microsoft Teams
- Permissions to use custom agents (may require admin approval)

### For Administrators
- Azure AI Foundry project with published agent
- Proper authentication and authorization setup
- Network access to Azure endpoints

## Integration Options

### 1. Microsoft Teams Integration

#### Accessing the Agent in Teams

1. **Open Microsoft Teams**
2. **Navigate to Apps**
   - Click on "Apps" in the left sidebar
   - Search for your custom agents or navigate to "Built for your org"

3. **Add the WeatherAgent**
   - Find "WeatherAgent" in the list
   - Click "Add" to add it to your Teams workspace

4. **Start a Conversation**
   - Click on the agent to open a chat
   - Ask weather-related questions naturally

#### Example Interactions in Teams

```
You: What's the weather like in Seattle?

WeatherAgent: Right now in Seattle, it's 12°C (54°F) with light rain. 
The humidity is at 78%, and there's a gentle breeze at 8 km/h. 
Don't forget your umbrella! ☔

You: How about Tokyo?

WeatherAgent: In Tokyo right now, it's 18°C (64°F) with clear skies. 
The humidity is 45%, and the wind is calm at 5 km/h. 
Perfect weather for outdoor activities! ☀️
```

### 2. Microsoft 365 Copilot Integration

#### Accessing via M365 Copilot

1. **Open Microsoft 365 Copilot**
   - Available in Word, PowerPoint, Outlook, or the Copilot app

2. **Invoke the WeatherAgent**
   - Type `@WeatherAgent` to mention the agent
   - Or enable it in your Copilot settings

3. **Ask Weather Questions**
   - Works across all M365 applications
   - Results can be inserted into documents

#### Example Use Cases

**In Word:**
```
You: @WeatherAgent What's the weather in Paris for my travel itinerary?

WeatherAgent: Currently in Paris, it's 15°C (59°F) with partly cloudy skies...
[Response can be inserted into your document]
```

**In Outlook:**
```
You: @WeatherAgent Should I schedule the outdoor meeting in New York tomorrow?

WeatherAgent: Current conditions in New York: 8°C (46°F), overcast...
[Helps you make scheduling decisions]
```

**In PowerPoint:**
```
You: @WeatherAgent Add current weather for our global offices

WeatherAgent: [Provides weather data that can be formatted as slides]
```

## Agent Capabilities

### What the Agent Can Do

✅ **Real-time Weather Data**
- Current temperature (Celsius and Fahrenheit)
- Weather conditions (sunny, cloudy, rainy, etc.)
- Humidity levels
- Wind speed
- Feels-like temperature

✅ **Global Coverage**
- Works for any city worldwide
- Supports various location formats (city names, "City, Country")

✅ **Conversational Context**
- Remembers previous questions in the conversation
- Can compare weather across multiple cities
- Natural language understanding

### What the Agent Cannot Do

❌ Weather forecasts (future predictions)
❌ Historical weather data
❌ Severe weather alerts
❌ Detailed meteorological analysis

## Technical Details

### API Endpoints

The published agent exposes two endpoints:

1. **Activity Protocol Endpoint**
   ```
   https://r2d2-foundry-001.services.ai.azure.com/api/projects/Main-Project/applications/WeatherAgent/protocols/activityprotocol?api-version=2025-11-15-preview
   ```
   - Used for Teams/M365 integration
   - Handles Activity Protocol messages

2. **Responses API Endpoint**
   ```
   https://r2d2-foundry-001.services.ai.azure.com/api/projects/Main-Project/applications/WeatherAgent/protocols/activityprotocol?api-version=2025-11-15-preview
   ```
   - Used for programmatic access
   - Direct API calls from custom applications

### Authentication

- Uses **Azure Active Directory (AAD)** authentication
- Requires **DefaultAzureCredential** for programmatic access
- Teams/M365 integration uses user's Microsoft 365 credentials

### Function Execution Model

**Important**: The agent defines what functions to call, but **function execution happens client-side**:

- **In Teams/M365**: Microsoft's platform executes the functions
- **In Custom Apps**: Your code must execute functions and return results
- **Security**: Functions run in a controlled environment with proper credentials

## Programmatic Access

If you want to call the published agent from your own Python code:

```python
# See: Foundry_Agents/call_published_agent.py

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

# Connect to the agent
with AIProjectClient(endpoint=endpoint, credential=credential) as client:
    openai_client = client.get_openai_client()
    
    # Create conversation
    conversation = openai_client.conversations.create(
        items=[{"type": "message", "role": "user", "content": "Weather in Paris?"}]
    )
    
    # Call published agent
    response = openai_client.responses.create(
        conversation=conversation.id,
        extra_body={
            "agent": {
                "name": "WeatherAgent",
                "version": "2",
                "type": "agent_reference"
            }
        },
        input=""
    )
```

## Permissions & Access Control

### User Permissions

Users need:
- Microsoft 365 Copilot license
- Access to custom agents (org policy)
- Network access to Azure endpoints

### Administrator Setup

1. **Publish the Agent**
   - Done via Azure AI Foundry portal
   - Select "Publish to Teams and Microsoft 365 Copilot"

2. **Configure Access**
   - Set who can use the agent (all users, specific groups, etc.)
   - Configure data access policies
   - Set up audit logging

3. **Monitor Usage**
   - Track agent invocations
   - Monitor function execution
   - Review error logs

## Best Practices

### For Users

✅ **Be Specific**: "Weather in Tokyo, Japan" vs "Tokyo"
✅ **Ask Follow-ups**: Agent maintains conversation context
✅ **Natural Language**: Ask questions normally, no special syntax needed

### For Administrators

✅ **Monitor Costs**: Track API calls to OpenWeatherMap
✅ **Set Quotas**: Implement rate limiting if needed
✅ **Update Regularly**: Keep agent version current
✅ **Test Changes**: Use development agents before publishing

## Troubleshooting

### Common Issues

**Agent Not Appearing in Teams**
- Verify publishing is complete
- Check user permissions
- Ensure org allows custom agents

**"Function execution failed" errors**
- Verify OPENWEATHER_API_KEY is set correctly
- Check network connectivity to OpenWeatherMap
- Review function execution logs

**Slow Responses**
- OpenWeatherMap API may be rate-limited
- Check network latency
- Consider caching recent queries

### Getting Help

- **Technical Issues**: Check Azure AI Foundry logs
- **Access Issues**: Contact your M365 administrator
- **API Issues**: Review OpenWeatherMap documentation

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 2 | 2026-01-22 | Published version with real OpenWeatherMap integration |
| 1 | 2026-01-22 | Initial development version |

## Related Documentation

- [Weather Agent Sync Implementation](../Foundry_Agents/weather_agent_sync.py)
- [Weather Agent Async Implementation](../Foundry_Agents/weather_agent_async.py)
- [Calling Published Agents](../Foundry_Agents/call_published_agent.py)
- [Deployment Guide](./DEPLOYMENT_GUIDE.md)

## Support

For questions or issues:
- **Repository**: https://github.com/Arturo-Quiroga-MSFT/BASIC_AGENTS_IN_FOUNDRY
- **Azure AI Foundry**: https://ai.azure.com
- **OpenWeatherMap API**: https://openweathermap.org/api

---

**Note**: This agent uses the OpenWeatherMap API which requires an API key. Ensure your `OPENWEATHER_API_KEY` environment variable is properly configured in your Azure AI Foundry project settings.
