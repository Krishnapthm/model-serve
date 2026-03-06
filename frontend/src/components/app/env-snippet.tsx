/** Env snippet display with copy-to-clipboard. */

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { IconCopy, IconCheck } from "@tabler/icons-react";
import { toast } from "sonner";

interface EnvSnippetProps {
  snippet: string;
}

export function EnvSnippet({ snippet }: EnvSnippetProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(snippet);
    setCopied(true);
    toast.success("Copied to clipboard");
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <Card className="bg-zinc-950 border-zinc-800">
      <CardContent className="p-4 relative">
        <pre className="text-sm text-zinc-300 font-mono whitespace-pre-wrap break-all">
          {snippet}
        </pre>
        <Button
          size="sm"
          variant="ghost"
          className="absolute top-3 right-3 text-zinc-400 hover:text-zinc-200"
          onClick={handleCopy}
        >
          {copied ? <IconCheck size={16} /> : <IconCopy size={16} />}
        </Button>
      </CardContent>
    </Card>
  );
}
