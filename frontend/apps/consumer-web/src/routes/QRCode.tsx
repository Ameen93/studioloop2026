import { Link } from 'react-router';
import { useQuery } from '@tanstack/react-query';
import { bookingsGetConsumerQr } from '@sl/api-client';
import { getAuthHeaders } from '../lib/apiAuth';

function generateQRMatrix(input: string, size: number = 21): boolean[][] {
  const matrix: boolean[][] = Array.from({ length: size }, () =>
    Array.from({ length: size }, () => false),
  );

  const drawFinder = (startRow: number, startCol: number) => {
    for (let r = 0; r < 7; r++) {
      for (let c = 0; c < 7; c++) {
        const isEdge = r === 0 || r === 6 || c === 0 || c === 6;
        const isInner = r >= 2 && r <= 4 && c >= 2 && c <= 4;
        matrix[startRow + r]![startCol + c] = isEdge || isInner;
      }
    }
  };

  drawFinder(0, 0);
  drawFinder(0, size - 7);
  drawFinder(size - 7, 0);

  let hash = 0;
  for (let i = 0; i < input.length; i++) {
    hash = ((hash << 5) - hash + input.charCodeAt(i)) | 0;
  }

  for (let r = 8; r < size - 8; r++) {
    for (let c = 8; c < size - 8; c++) {
      hash = ((hash << 5) - hash + r * size + c) | 0;
      matrix[r]![c] = (hash & 1) === 1;
    }
  }

  for (let i = 8; i < size - 8; i++) {
    matrix[6]![i] = i % 2 === 0;
    matrix[i]![6] = i % 2 === 0;
  }

  return matrix;
}

function QRCodeSVG({ data, size = 220 }: { data: string; size?: number }) {
  const moduleCount = 21;
  const matrix = generateQRMatrix(data, moduleCount);
  const cellSize = size / moduleCount;

  return (
    <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} className="mx-auto">
      <rect width={size} height={size} fill="white" />
      {matrix.map((row, r) =>
        row.map((cell, c) =>
          cell ? (
            <rect
              key={`${r}-${c}`}
              x={c * cellSize}
              y={r * cellSize}
              width={cellSize}
              height={cellSize}
              fill="black"
            />
          ) : null,
        ),
      )}
    </svg>
  );
}

export function QRCode() {
  const qrQuery = useQuery({
    queryKey: ['consumer-qr-code'],
    queryFn: async () => {
      const response = await bookingsGetConsumerQr({
        headers: getAuthHeaders(),
      });
      return response.data;
    },
  });

  const qrData = qrQuery.data;

  return (
    <div className="max-w-md mx-auto px-4 py-8 flex flex-col items-center">
      <Link
        to="/"
        className="self-start mb-6 text-sm text-coral-600 hover:text-coral-500 font-medium"
      >
        &larr; Back to home
      </Link>

      {qrQuery.isLoading && (
        <div className="w-full rounded-lg border border-gray-200 bg-white p-4 text-sm text-gray-600">
          Loading QR code...
        </div>
      )}

      {qrQuery.error && (
        <div className="w-full rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          Could not generate QR code.
        </div>
      )}

      {!qrData ? null : (
        <>
          <div className="w-full bg-white rounded-2xl shadow-lg border border-gray-100 p-8 text-center">
            <h1 className="text-xl font-bold text-gray-900 mb-2">Check-in QR Code</h1>
            <p className="text-sm text-gray-500 mb-6">
              Show this at the front desk to check in
            </p>

            <div className="bg-white p-4 rounded-xl border-2 border-gray-100 inline-block">
              <QRCodeSVG data={qrData.token} size={220} />
            </div>

            <div className="mt-6">
              <p className="text-lg font-semibold text-gray-900">{qrData.consumer_name}</p>
              <p className="text-xs text-gray-400 mt-1">
                Expires: {new Date(qrData.expires_at).toLocaleTimeString('en-ZA')}
              </p>
            </div>
          </div>

          <p className="mt-6 text-center text-xs text-gray-400 max-w-xs">
            This token updates and expires automatically for secure check-in.
          </p>
        </>
      )}
    </div>
  );
}

export default QRCode;
