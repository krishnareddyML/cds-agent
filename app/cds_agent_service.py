import asyncio
import os
from dataclasses import dataclass
from typing import Any, List

import logfire
from devtools import debug
from httpx import AsyncClient
from pydantic_ai.usage import Usage, UsageLimits

from pydantic_ai import Agent, ModelRetry, RunContext
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.models.mistral import MistralModel
from app.cds_agent_models import CdsAgentInput, CdsAgentOutput, Deps, PatientVitals, PatientLabs, PatientMedications, PatientAllergies, PatientDemographics, PatientProblems


class CdsAgentService:

    falcon_base_url = os.getenv('EMR_BASE_URL', 'https://api.emr.com/v1')

    #configure logfire
    logfire.configure(token=os.getenv('LOGFIRE_CDSS_AGENT_TOKEN'))
    logfire.instrument_openai()
    
    model = OpenAIModel(
        model_name=os.getenv('DEFAULT_MODEL_NAME', 'mistral:latest'),
        base_url=os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434/v1'),
        api_key=os.getenv('OLLAMA_API_KEY', 'OLLAMA_LOCAL')        
    )

    #model = OpenAIModel("gpt-4o-mini")
    #model = MistralModel('mistral-small-latest', api_key='your_api_key')
    
    system_prompt=(
        f"""
        You are an AI assistant designed to assist physicians in determining whether a patient meets a specific clinical criterion.  
To do this, you must retrieve the necessary patient data using available functions and analyze it against physician provided question.
 
You can only call functions according to the following formatting rules:  

Rule 1: All the functions you have access to are contained within {{tool_list_start}}{{tool_list_end}} XML tags. You cannot use any functions that are not listed between these tags.    

Rule 2: For each function call, output JSON which conforms to the schema of the function. You must wrap the function call in {{tool_call_start}}[...list of tool calls...]{{tool_call_end}} XML tags. Each call will be a JSON object with the keys "name" and "arguments". The "name" key will contain the name of the function you are calling, and the "arguments" key will contain the arguments you are passing to the function as a JSON object. The top level structure is a list of these objects. YOU MUST OUTPUT VALID JSON BETWEEN THE {{tool_call_start}} AND {{tool_call_end}} TAGS!    

 Rule 3: If user decides to run the function, they will output the result of the function call in the following query. If it answers the user's question, you should incorporate the output of the function in your following message.
          

Respond only in the following format:

```json
{{
  "CriteriaMet": "Yes/No",
  "explanation": [
    "Reason 1",
    "Reason 2",
    "Reason 3"
  ]
}}
          """
                    )

    cdss_agent = Agent(model=model, system_prompt=system_prompt, result_retries=3)
       
    
    @cdss_agent.tool
    async def get_vitals(ctx: RunContext[Deps], visit_id: str) -> List[PatientVitals]:
        """Get the All Vitlas of a patient.

        Args:
            ctx: The context.
            visit_id: The visit id of the patient.
            
        """
        if ctx.deps.falconApiKey is None:
            return [PatientVitals(visitId=visit_id, vitalName='BP', vitalResult='120/80'),
                    PatientVitals(visitId=visit_id, vitalName='Heart Rate', vitalResult='98'),
                    PatientVitals(visitId=visit_id, vitalName='Temperature', vitalResult='98.6'),
                    PatientVitals(visitId=visit_id, vitalName='Respiratory Rate', vitalResult='16'),
                    PatientVitals(visitId=visit_id, vitalName='Oxygen Saturation', vitalResult='98'),
                    PatientVitals(visitId=visit_id, vitalName='Weight', vitalResult='100'),
                    ]
        
        headers = {
            'Authorization': f'Bearer {ctx.deps.falconApiKey}',
            'Content-Type': 'application/json'
        }
        payload = {
            'visitId': visit_id,
            #'vitalName': vital_name
        }
        with logfire.span('calling Vitals API', params=payload) as span:
            r = await ctx.deps.client.post(CdsAgentService.falcon_base_url+'/vitals', headers=headers, json=payload)
            r.raise_for_status()
            data = r.json()
            
            if data:
                span.set_attribute('response', data)
                return data
            else:
                raise ModelRetry('Could not find the vitals, skip using vitals')

    @cdss_agent.tool
    async def get_vital_by_name(ctx: RunContext[Deps], visit_id: str, vital_name:str) -> PatientVitals:
        """Get the Vitlas of a patient by target vital name.

        Args:
            ctx: The context.
            visit_id: The visit id of the patient.
            vital_name: The name of the vital to be retrieved
            
        """
        if ctx.deps.falconApiKey is None:
            if vital_name == 'BP':
               return PatientVitals(visitId=visit_id, vitalName='BP', vitalResult='120/80')
            elif vital_name == 'Heart Rate':
                return PatientVitals(visitId=visit_id, vitalName='Heart Rate', vitalResult='98')
            elif vital_name == 'Temperature':
                return PatientVitals(visitId=visit_id, vitalName='Temperature', vitalResult='98.6')
            elif vital_name == 'Respiratory Rate':
                return PatientVitals(visitId=visit_id, vitalName='Respiratory Rate', vitalResult='16')
            elif vital_name == 'Oxygen Saturation':
                return PatientVitals(visitId=visit_id, vitalName='Oxygen Saturation', vitalResult='98')
            elif vital_name == 'weight':
                return PatientVitals(visitId=visit_id, vitalName='Weight', vitalResult='100')
            else:
                raise ModelRetry('Could not find the vitals, use get_vitals method to get all vitals')    
        
        headers = {
            'Authorization': f'Bearer {ctx.deps.falconApiKey}',
            'Content-Type': 'application/json'
        }
        payload = {
            'visitId': visit_id,
            'vitalName': vital_name
        }
        with logfire.span('calling Vitals API', params=payload) as span:
            r = await ctx.deps.client.post(CdsAgentService.falcon_base_url+'/vitals', headers=headers, json=payload)
            r.raise_for_status()
            data = r.json()
            
            if data:
                span.set_attribute('response', data)
                return data
            else:
                raise ModelRetry('Could not find the vitals, use get_vitals method to get all vitals')        

    @cdss_agent.tool
    async def get_lab_result(ctx: RunContext[Deps], visit_id: str) -> List[PatientLabs]:
        """Get the lab results of a patient.

        Args:
            ctx: The context.
            visit_id: The visit id of the patient.
            
        """
        if ctx.deps.falconApiKey is None:
            return [PatientLabs(visitId=visit_id, labTestName='CBC', labResult='Normal'),
                    PatientLabs(visitId=visit_id, labTestName='CMP', labResult='Normal'),
                    PatientLabs(visitId=visit_id, labTestName='Lipid Profile', labResult='Normal'),
                    PatientLabs(visitId=visit_id, labTestName='Urine Analysis', labResult='Normal'),
                    PatientLabs(visitId=visit_id, labTestName='HbA1c', labResult='5.2'),
                    PatientLabs(visitId=visit_id, labTestName='WBC', labResult='12.5'),
                    ]
        
        headers = {
            'Authorization': f'Bearer {ctx.deps.falconApiKey}',
            'Content-Type': 'application/json'
        }
        payload = {
            'visitId': visit_id,
            #'labTestName': test_name
        }
        r = await ctx.deps.client.post(CdsAgentService.falcon_base_url+'/labs', headers=headers, json=payload)
        r.raise_for_status()
        data = r.json()
        
        if data:
            return data
        else:
            raise ModelRetry('Could not find the lab results')
        
    @cdss_agent.tool
    async def get_medications(ctx: RunContext[Deps], visit_id: str) -> List[PatientMedications]:
        """Get the medications of a patient.

        Args:
            ctx: The context.
            visit_id: The visit id of the patient.
            
        """
        if ctx.deps.falconApiKey is None:
            return [PatientMedications(visitId=visit_id, medicationName='Metformin', medicationDose='500mg'),
                    PatientMedications(visitId=visit_id, medicationName='Lisinopril', medicationDose='10mg'),
                    PatientMedications(visitId=visit_id, medicationName='Atorvastatin', medicationDose='20mg'),
                    PatientMedications(visitId=visit_id, medicationName='Aspirin', medicationDose='81mg'),
                    PatientMedications(visitId=visit_id, medicationName='Levothyroxine', medicationDose='50mcg'),
                    ]
        
        headers = {
            'Authorization': f'Bearer {ctx.deps.falconApiKey}',
            'Content-Type': 'application/json'
        }
        payload = {
            'visitId': visit_id,
            #'medicationName': medication_name
        }
        r = await ctx.deps.client.post(CdsAgentService.falcon_base_url+'/medications', headers=headers, json=payload)
        r.raise_for_status()
        data = r.json()
        
        if data:
            return data
        else:
            raise ModelRetry('Could not find the medications')
    @cdss_agent.tool
    async def get_allergies(ctx: RunContext[Deps], visit_id: str) -> List[PatientAllergies]:
        """Get the allergies of a patient.

        Args:
            ctx: The context.
            visit_id: The visit id of the patient.
            
        """
        if ctx.deps.falconApiKey is None:
            return [PatientAllergies(visitId=visit_id, allergyName='Penicillin', allergySeverity='Mild'),
                    PatientAllergies(visitId=visit_id, allergyName='Sulfa', allergySeverity='Severe'),
                    PatientAllergies(visitId=visit_id, allergyName='Codeine', allergySeverity='Mild'),
                    PatientAllergies(visitId=visit_id, allergyName='Aspirin', allergySeverity='Severe'),
                    PatientAllergies(visitId=visit_id, allergyName='Latex', allergySeverity='Mild'),
                    ]
        
        headers = {
            'Authorization': f'Bearer {ctx.deps.falconApiKey}',
            'Content-Type': 'application/json'
        }
        payload = {
            'visitId': visit_id,            
        }
        r = await ctx.deps.client.post(CdsAgentService.falcon_base_url+'/allergies', headers=headers, json=payload)
        r.raise_for_status()
        data = r.json()
        
        if data:
            return data
        else:
            raise ModelRetry('Could not find the allergies')
        
    @cdss_agent.tool
    async def get_demo_graphics(ctx: RunContext[Deps], visit_id: str) -> PatientDemographics:
        """Get the demographics of a patient.

        Args:
            ctx: The context.
            visit_id: The visit id of the patient.
        """
        if ctx.deps.falconApiKey is None:
            return PatientDemographics(visitId=visit_id, patientName='John Doe', patientAge='45', patientGender='F',
                                        patientRace='White', patientEthnicity='Non-Hispanic')
        
        headers = {
            'Authorization': f'Bearer {ctx.deps.falconApiKey}',
            'Content-Type': 'application/json'
        }
        payload = {
            'visitId': visit_id            
        }
        r = await ctx.deps.client.post(CdsAgentService.falcon_base_url+'/demographics', headers=headers, json=payload)
        r.raise_for_status()
        data = r.json()
        
        if data:
            return data
        else:
            raise ModelRetry('Could not find the demographics')

    @cdss_agent.tool
    async def get_problems_list(ctx: RunContext[Deps], visit_id: str) -> List[PatientProblems]:
        """Get the problems list of a patient.

        Args:
            ctx: The context.
            visit_id: The visit id of the patient.            
        """
        if ctx.deps.falconApiKey is None:
            print('Yes Falcon API Key is None', ctx.deps.falconApiKey)
            return [PatientProblems(visitId=visit_id, problemName='Hypertension', problemSeverity='Mild'),
                    PatientProblems(visitId=visit_id, problemName='Diabetes', problemSeverity='Severe'),
                    PatientProblems(visitId=visit_id, problemName='Hyperlipidemia', problemSeverity='Mild'),
                    PatientProblems(visitId=visit_id, problemName='Obesity', problemSeverity='Severe'),
                    PatientProblems(visitId=visit_id, problemName='Asthma', problemSeverity='Mild'),
                    ]
        
        headers = {
            'Authorization': f'Bearer {ctx.deps.falconApiKey}',
            'Content-Type': 'application/json'
        }
        payload = {
            'visitId': visit_id,            
        }
        r = await ctx.deps.client.post(CdsAgentService.falcon_base_url+'/problems', headers=headers, json=payload)
        r.raise_for_status()
        data = r.json()
        
        if data:
            return data
        else:
            raise ModelRetry('Could not find the problems list')    

    def get_falcon_api_key():
        return os.getenv('FALCON_API_KEY')

    async def run(agent_input: CdsAgentInput) -> str:
        usage: Usage = Usage()
        usage_limits = UsageLimits(request_limit=20)
        
        async with AsyncClient() as client:
            falcon_api_key = CdsAgentService.get_falcon_api_key()
            deps = Deps(client=client, falconApiKey=falcon_api_key)
            
            result = await CdsAgentService.cdss_agent.run(
                agent_input.cdssQuery+' For the Patient Visit:'+agent_input.visitId,
                deps=deps,
                result_type=str,
                usage=usage,
                usage_limits=usage_limits,
                )
            
            debug(result)
            print('Response:', result.data)
            return result.data