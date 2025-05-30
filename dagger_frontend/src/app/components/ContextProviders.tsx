"use client";
import React from 'react';
import { AuthProvider } from '../contexts/auth_context';
import { TeamProvider } from '../contexts/team_context';
import { DagProvider } from '../contexts/dag_context';
import { DataProvider } from '../contexts/data_context';
import { ReactFlowProvider } from 'reactflow';

interface ContextProvidersProps {
  children: React.ReactNode;
}

const ContextProviders: React.FC<ContextProvidersProps> = ({ children }) => (
  <AuthProvider>
    <TeamProvider>
      <DagProvider>
        <DataProvider>
          <ReactFlowProvider>
            {children}
          </ReactFlowProvider>
        </DataProvider>
      </DagProvider>
    </TeamProvider>
  </AuthProvider>
);

export default ContextProviders; 