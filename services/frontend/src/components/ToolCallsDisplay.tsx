import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Wrench, CheckCircle2 } from 'lucide-react';

interface ToolCall {
  tool: string;
  args: Record<string, unknown>;
}

interface ToolResult {
  tool: string;
  result: unknown;
}

interface ToolCallsDisplayProps {
  toolCalls?: ToolCall[];
  toolResults?: ToolResult[];
}

export function ToolCallsDisplay({ toolCalls, toolResults }: ToolCallsDisplayProps) {
  if (!toolCalls || toolCalls.length === 0) {
    return null;
  }

  return (
    <Card className="bg-gray-800/50 border-gray-700 p-4 space-y-3">
      <div className="flex items-center gap-2 text-purple-400">
        <Wrench className="w-4 h-4" />
        <span className="text-sm font-semibold">Tool-Aufrufe</span>
      </div>
      
      {toolCalls.map((call, index) => {
        const result = toolResults?.find(r => r.tool === call.tool);
        
        return (
          <div key={index} className="border-l-2 border-purple-500/50 pl-3 space-y-2">
            <div className="flex items-center gap-2">
              <Badge className="bg-purple-600 text-white text-xs">
                {call.tool}
              </Badge>
              {result && (
                <CheckCircle2 className="w-3 h-3 text-green-500" />
              )}
            </div>
            
            {Object.keys(call.args).length > 0 && (
              <div className="text-xs">
                <span className="text-gray-500">Parameter: </span>
                <span className="text-gray-300 font-mono">
                  {JSON.stringify(call.args)}
                </span>
              </div>
            )}
            
            {result && (
              <div className="text-xs">
                <span className="text-gray-500">Ergebnis: </span>
                <span className="text-gray-300 font-mono">
                  {typeof result.result === 'object' 
                    ? JSON.stringify(result.result, null, 2)
                    : String(result.result)}
                </span>
              </div>
            )}
          </div>
        );
      })}
    </Card>
  );
}
