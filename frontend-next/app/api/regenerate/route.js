import { spawn } from 'child_process';
import path from 'path';
import { readFile } from 'fs/promises';

const PROJECT_ROOT = path.resolve(process.cwd(), '..');
const PYTHON = path.join(PROJECT_ROOT, '.venv', 'bin', 'python');

export async function POST(request) {
  const { week } = await request.json().catch(() => ({}));
  const isoWeek = week || getCurrentIsoWeek();

  return new Promise((resolve) => {
    const args = [
      '-m', 'groww_pulse', 'run',
      '--week', isoWeek,
      '--dry-run',
      '--export-frontend',
    ];

    const proc = spawn(PYTHON, args, {
      cwd: PROJECT_ROOT,
      env: { ...process.env },
    });

    let stdout = '';
    let stderr = '';

    proc.stdout.on('data', (d) => { stdout += d.toString(); });
    proc.stderr.on('data', (d) => { stderr += d.toString(); });

    proc.on('close', async (code) => {
      if (code !== 0) {
        resolve(
          new Response(
            JSON.stringify({ error: 'Pipeline failed', details: stderr + stdout }),
            { status: 500, headers: { 'Content-Type': 'application/json' } }
          )
        );
        return;
      }

      try {
        const jsonPath = path.join(PROJECT_ROOT, 'data', 'frontend_output.json');
        const raw = await readFile(jsonPath, 'utf-8');
        resolve(
          new Response(raw, {
            status: 200,
            headers: { 'Content-Type': 'application/json' },
          })
        );
      } catch (err) {
        resolve(
          new Response(
            JSON.stringify({ error: 'Could not read output file', details: err.message }),
            { status: 500, headers: { 'Content-Type': 'application/json' } }
          )
        );
      }
    });
  });
}

function getCurrentIsoWeek() {
  const now = new Date();
  const date = new Date(Date.UTC(now.getFullYear(), now.getMonth(), now.getDate()));
  date.setUTCDate(date.getUTCDate() + 4 - (date.getUTCDay() || 7));
  const yearStart = new Date(Date.UTC(date.getUTCFullYear(), 0, 1));
  const weekNo = Math.ceil(((date - yearStart) / 86400000 + 1) / 7);
  return `${date.getUTCFullYear()}-W${String(weekNo).padStart(2, '0')}`;
}
