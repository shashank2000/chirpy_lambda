export async function fetchResult(
  input: string | undefined,
  reset = false,
  kwargs: object = {}
) {
  const response = await fetch(
    'http://localhost:8765/api/ping?' +
      new URLSearchParams({
        input: String(input),
        reset: String(reset),
        kwargs: JSON.stringify(kwargs)
      })
  );
  if (response.status == 500) {
    alert('Server error.');
    return;
  }
  const data = await response.json();
  return data;
}

export async function fetchSupernodes() {
  const response = await fetch('http://localhost:8765/api/supernodes');
  if (response.status == 500) {
    alert('Server error.');
    return;
  }
  const data = await response.json();
  return data as { supernodes: string[] };
}
