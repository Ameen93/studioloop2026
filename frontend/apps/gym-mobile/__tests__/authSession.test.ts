import { emitSessionExpired, onSessionExpired } from '../lib/authSession';

describe('gym mobile authSession', () => {
  it('notifies listeners on session expiry', () => {
    const listener = jest.fn();
    const unsubscribe = onSessionExpired(listener);

    emitSessionExpired();
    expect(listener).toHaveBeenCalledTimes(1);

    unsubscribe();
    emitSessionExpired();
    expect(listener).toHaveBeenCalledTimes(1);
  });
});
