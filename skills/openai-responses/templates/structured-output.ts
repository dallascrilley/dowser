/**
 * Structured Output Response
 *
 * End-to-end example of constraining a model response
 * to a JSON schema using Structured Outputs (Responses API).
 */

import OpenAI from 'openai';
import { zodTextFormat } from 'openai/helpers/zod';
import { z } from 'zod';

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

async function structuredOutput() {
  // Schema-enforced structured output using Structured Outputs
  const SupportTicket = z
    .object({
      subject: z.string().describe('Short title for the support ticket'),
      priority: z.enum(['low', 'medium', 'high']),
      impact: z.enum(['individual', 'team', 'company']),
      summary: z.string().describe('2-3 sentence summary of the issue'),
      steps_to_reproduce: z
        .array(z.string())
        .min(1)
        .describe('Ordered steps that recreate the issue'),
      suggested_fix: z
        .string()
        .describe('Best guess at resolution or mitigation')
        .nullable(),
    })
    .strict();

  const response = await openai.responses.parse({
    model: 'gpt-4o-2024-08-06', // Structured Outputs requires supported models
    input: [
      {
        role: 'system',
        content:
          'You are a support triage assistant. Convert the user report into a structured ticket.',
      },
      {
        role: 'user',
        content:
          'The dashboard keeps timing out for our sales reps when they try to export more than 500 rows. They need this for weekly reporting tomorrow.',
      },
    ],
    text: {
      format: zodTextFormat(SupportTicket, 'support_ticket'),
    },
  });

  if (response.status === 'incomplete') {
    console.warn('Structured response incomplete:', response.incomplete_details);
    return;
  }

  const ticket = response.output_parsed;
  console.log(ticket);
  console.log('Priority:', ticket.priority);
}

// Run examples
structuredOutput();
