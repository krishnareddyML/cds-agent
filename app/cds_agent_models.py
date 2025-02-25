from dataclasses import dataclass
from httpx import AsyncClient
from pydantic import BaseModel, Field
from typing import List
from enum import Enum

class CdsAgentInput(BaseModel):
    visitId: str
    cdssQuery: str
    modelName: str

class CdsAgentOutput(BaseModel):
    criteriaMet: bool = Field(..., description="Indicates whether the required criteria have been met.")
    explanation: List[str] = Field(..., description="List of explanations detailing how the criteria were evaluated. include each criteria met or not.")

@dataclass
class Deps:
    client: AsyncClient
    falconApiKey: str

class PatientVitals(BaseModel):
    visitId: str
    vitalName: str
    vitalResult: str

class PatientLabs(BaseModel):
    visitId: str
    labTestName: str
    labResult: str

class PatientMedications(BaseModel):
    visitId: str
    medicationName: str
    medicationDose: str

class PatientAllergies(BaseModel):
    visitId: str
    allergyName: str
    allergySeverity: str

class PatientDemographics(BaseModel):
    visitId: str
    patientName: str
    patientAge: str
    patientGender: str
    patientRace: str
    patientEthnicity: str

class PatientProblems(BaseModel):
    visitId: str
    problemName: str
    problemSeverity: str
