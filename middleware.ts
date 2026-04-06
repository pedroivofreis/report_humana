import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

const REALM = 'Humana';
const EXPECTED_PASSWORD = process.env.RELATORIO_PASSWORD ?? 'Humana';

export function middleware(request: NextRequest) {
  // Em `next dev` o relatório abre direto; em produção (Vercel) a senha continua obrigatória.
  if (process.env.NODE_ENV === 'development') {
    return NextResponse.next();
  }

  const auth = request.headers.get('authorization');
  if (auth?.startsWith('Basic ')) {
    try {
      const decoded = atob(auth.slice(6));
      const colon = decoded.indexOf(':');
      const password = colon >= 0 ? decoded.slice(colon + 1) : '';
      if (password === EXPECTED_PASSWORD) {
        return NextResponse.next();
      }
    } catch {
      /* invalid base64 */
    }
  }

  return new NextResponse('Autenticação necessária.', {
    status: 401,
    headers: {
      'WWW-Authenticate': `Basic realm="${REALM}"`,
    },
  });
}

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico).*)'],
};
